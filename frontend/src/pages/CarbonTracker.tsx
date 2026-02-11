import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { 
  Leaf, ArrowLeft, Zap, TreePine, TrendingDown, 
  TrendingUp, Loader2, BarChart3, Car, Plane
} from 'lucide-react';
import { api, CarbonMetric } from '@/lib/api';
import * as d3 from 'd3';

interface CarbonStats {
  total_carbon_kg: number;
  total_trees_planted: number;
  carbon_offset_kg: number;
  net_carbon_kg: number;
  is_carbon_positive: boolean;
}

export default function CarbonTracker() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [carbonMetrics, setCarbonMetrics] = useState<CarbonMetric[]>([]);
  const [carbonStats, setCarbonStats] = useState<CarbonStats | null>(null);
  const chartRef = useRef<SVGSVGElement>(null);
  const pieChartRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    checkAuthAndLoad();
  }, []);

  useEffect(() => {
    if (carbonMetrics.length > 0 && chartRef.current) {
      drawBarChart();
    }
    if (carbonStats && pieChartRef.current) {
      drawPieChart();
    }
  }, [carbonMetrics, carbonStats]);

  const checkAuthAndLoad = async () => {
    try {
      const user = await api.verifyAuth();
      if (!user) {
        navigate('/login');
        return;
      }
      await loadData();
    } catch {
      navigate('/login');
    }
  };

  const loadData = async () => {
    try {
      const [metricsRes, statsRes] = await Promise.all([
        api.getCarbonMetrics(),
        api.getCarbonStats()
      ]);
      
      if (metricsRes?.items) {
        setCarbonMetrics(metricsRes.items);
      }
      
      if (statsRes) {
        setCarbonStats(statsRes);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const drawBarChart = () => {
    if (!chartRef.current || carbonMetrics.length === 0) return;

    const svg = d3.select(chartRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 20, bottom: 40, left: 50 };
    const width = 600 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const g = svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Group data by date
    const groupedData = d3.rollup(
      carbonMetrics,
      v => d3.sum(v, d => d.carbon_footprint),
      d => new Date(d.session_date).toLocaleDateString('fr-FR')
    );

    const data = Array.from(groupedData, ([date, value]) => ({ date, value })).slice(-7);

    const x = d3.scaleBand()
      .domain(data.map(d => d.date))
      .range([0, width])
      .padding(0.3);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value) || 100])
      .nice()
      .range([height, 0]);

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('fill', '#065f46')
      .attr('font-size', '10px');

    // Y axis
    g.append('g')
      .call(d3.axisLeft(y).ticks(5))
      .selectAll('text')
      .attr('fill', '#065f46');

    // Bars
    g.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.date) || 0)
      .attr('y', d => y(d.value))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.value))
      .attr('fill', '#10b981')
      .attr('rx', 4);

    // Y axis label
    g.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -40)
      .attr('x', -height / 2)
      .attr('text-anchor', 'middle')
      .attr('fill', '#065f46')
      .attr('font-size', '12px')
      .text('CO₂ (g)');
  };

  const drawPieChart = () => {
    if (!pieChartRef.current || !carbonStats) return;

    const svg = d3.select(pieChartRef.current);
    svg.selectAll('*').remove();

    const width = 200;
    const height = 200;
    const radius = Math.min(width, height) / 2;

    const g = svg
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', `translate(${width / 2},${height / 2})`);

    const data = [
      { label: 'Émis', value: carbonStats.total_carbon_kg, color: '#f59e0b' },
      { label: 'Compensé', value: carbonStats.carbon_offset_kg, color: '#10b981' }
    ];

    const pie = d3.pie<{ label: string; value: number; color: string }>()
      .value(d => d.value)
      .sort(null);

    const arc = d3.arc<d3.PieArcDatum<{ label: string; value: number; color: string }>>()
      .innerRadius(radius * 0.5)
      .outerRadius(radius * 0.9);

    g.selectAll('path')
      .data(pie(data))
      .enter()
      .append('path')
      .attr('d', arc)
      .attr('fill', d => d.data.color)
      .attr('stroke', 'white')
      .attr('stroke-width', 2);

    // Center text
    g.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '-0.2em')
      .attr('fill', carbonStats.is_carbon_positive ? '#10b981' : '#f59e0b')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text(carbonStats.is_carbon_positive ? 'Positif!' : 'À compenser');

    g.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '1.2em')
      .attr('fill', '#065f46')
      .attr('font-size', '10px')
      .text(`${Math.abs(carbonStats.net_carbon_kg).toFixed(2)} kg`);
  };

  const handlePlantTree = async () => {
    try {
      const response = await api.plantTree();
      if (response?.success) {
        toast({
          title: "🌳 Arbre planté!",
          description: "Merci pour votre contribution à la reforestation!"
        });
        await loadData();
      }
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de planter l'arbre",
        variant: "destructive"
      });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100 flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-emerald-600" />
      </div>
    );
  }

  const stats = carbonStats || {
    total_carbon_kg: 0,
    total_trees_planted: 0,
    carbon_offset_kg: 0,
    net_carbon_kg: 0,
    is_carbon_positive: true
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-emerald-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/dashboard')}
            className="text-emerald-700"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Retour
          </Button>
          <div className="flex items-center gap-2">
            <Leaf className="h-6 w-6 text-emerald-600" />
            <span className="font-semibold text-emerald-800">Suivi Carbone</span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Image */}
        <Card className="bg-white/80 backdrop-blur border-emerald-200 mb-8 overflow-hidden">
          <div className="relative h-48">
            <img 
              src="https://mgx-backend-cdn.metadl.com/generate/images/963879/2026-02-10/73af077f-0589-42bb-8143-0ff654c987fa.png"
              alt="Carbon Footprint"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-900/80 to-transparent flex items-center">
              <div className="p-8">
                <h1 className="text-3xl font-bold text-white mb-2">Votre Impact Environnemental</h1>
                <p className="text-emerald-100">Suivez et compensez votre empreinte carbone</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-white/80 backdrop-blur border-emerald-200">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-3 bg-amber-100 rounded-xl">
                <Zap className="h-6 w-6 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-emerald-600">CO₂ émis</p>
                <p className="text-2xl font-bold text-emerald-900">{(stats.total_carbon_kg * 1000).toFixed(0)}g</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/80 backdrop-blur border-emerald-200">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-xl">
                <TreePine className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-emerald-600">CO₂ compensé</p>
                <p className="text-2xl font-bold text-emerald-900">{stats.carbon_offset_kg.toFixed(1)}kg</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/80 backdrop-blur border-emerald-200">
            <CardContent className="p-4 flex items-center gap-4">
              <div className={`p-3 rounded-xl ${stats.is_carbon_positive ? 'bg-green-100' : 'bg-amber-100'}`}>
                {stats.is_carbon_positive ? (
                  <TrendingDown className="h-6 w-6 text-green-600" />
                ) : (
                  <TrendingUp className="h-6 w-6 text-amber-600" />
                )}
              </div>
              <div>
                <p className="text-sm text-emerald-600">Bilan net</p>
                <p className={`text-2xl font-bold ${stats.is_carbon_positive ? 'text-green-600' : 'text-amber-600'}`}>
                  {stats.net_carbon_kg.toFixed(2)}kg
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/80 backdrop-blur border-emerald-200">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-3 bg-emerald-100 rounded-xl">
                <TreePine className="h-6 w-6 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm text-emerald-600">Arbres plantés</p>
                <p className="text-2xl font-bold text-emerald-900">{stats.total_trees_planted}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Bar Chart */}
          <Card className="lg:col-span-2 bg-white/80 backdrop-blur border-emerald-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-emerald-900">
                <BarChart3 className="h-5 w-5" />
                Émissions par jour
              </CardTitle>
              <CardDescription className="text-emerald-600">
                Votre empreinte carbone des 7 derniers jours
              </CardDescription>
            </CardHeader>
            <CardContent>
              {carbonMetrics.length > 0 ? (
                <svg ref={chartRef} className="w-full"></svg>
              ) : (
                <div className="h-64 flex items-center justify-center text-emerald-600">
                  Aucune donnée disponible
                </div>
              )}
            </CardContent>
          </Card>

          {/* Pie Chart & Action */}
          <div className="space-y-6">
            <Card className="bg-white/80 backdrop-blur border-emerald-200">
              <CardHeader>
                <CardTitle className="text-emerald-900">Bilan carbone</CardTitle>
              </CardHeader>
              <CardContent className="flex justify-center">
                <svg ref={pieChartRef}></svg>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-emerald-500 to-green-600 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TreePine className="h-5 w-5" />
                  Plantez un arbre
                </CardTitle>
                <CardDescription className="text-emerald-100">
                  Compensez votre empreinte carbone
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-emerald-100 mb-4">
                  Un arbre absorbe environ 21kg de CO₂ par an
                </p>
                <Button 
                  onClick={handlePlantTree}
                  className="w-full bg-white text-emerald-600 hover:bg-emerald-50"
                >
                  🌳 Planter un arbre
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Equivalences */}
        <Card className="bg-white/80 backdrop-blur border-emerald-200 mt-8">
          <CardHeader>
            <CardTitle className="text-emerald-900">Équivalences</CardTitle>
            <CardDescription className="text-emerald-600">
              Votre empreinte carbone en perspective
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="flex items-center gap-4 p-4 bg-emerald-50 rounded-xl">
                <div className="p-3 bg-emerald-100 rounded-full">
                  <Car className="h-8 w-8 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm text-emerald-600">Équivalent voiture</p>
                  <p className="text-2xl font-bold text-emerald-900">
                    {(stats.total_carbon_kg / 0.12).toFixed(1)} km
                  </p>
                  <p className="text-xs text-emerald-500">basé sur 120g CO₂/km</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4 p-4 bg-emerald-50 rounded-xl">
                <div className="p-3 bg-emerald-100 rounded-full">
                  <Plane className="h-8 w-8 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm text-emerald-600">Équivalent vol Paris-NY</p>
                  <p className="text-2xl font-bold text-emerald-900">
                    {(stats.total_carbon_kg / 1000).toFixed(4)}
                  </p>
                  <p className="text-xs text-emerald-500">basé sur ~1 tonne CO₂/vol</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}