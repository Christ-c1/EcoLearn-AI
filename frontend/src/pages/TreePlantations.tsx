import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { 
  Leaf, ArrowLeft, TreePine, MapPin, Calendar, 
  Award, Loader2, Globe, Sprout
} from 'lucide-react';
import { api, TreePlantation } from '@/lib/api';

export default function TreePlantations() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [plantations, setPlantations] = useState<TreePlantation[]>([]);
  const [totalTrees, setTotalTrees] = useState(0);
  const [totalOffset, setTotalOffset] = useState(0);

  useEffect(() => {
    checkAuthAndLoad();
  }, []);

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
      const response = await api.getTreePlantations();
      if (response?.items) {
        setPlantations(response.items);
        const trees = response.items.reduce((sum: number, p: TreePlantation) => sum + p.trees_planted, 0);
        const offset = response.items.reduce((sum: number, p: TreePlantation) => sum + p.carbon_offset, 0);
        setTotalTrees(trees);
        setTotalOffset(offset);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setIsLoading(false);
    }
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

  const locationColors: Record<string, string> = {
    'France': 'bg-blue-100 text-blue-700',
    'Brésil': 'bg-green-100 text-green-700',
    'Kenya': 'bg-orange-100 text-orange-700',
    'Indonésie': 'bg-red-100 text-red-700',
    'Canada': 'bg-purple-100 text-purple-700'
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
            <span className="font-semibold text-emerald-800">Mes Arbres</span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero */}
        <Card className="bg-white/80 backdrop-blur border-emerald-200 mb-8 overflow-hidden">
          <div className="relative h-64">
            <img 
              src="https://mgx-backend-cdn.metadl.com/generate/images/963879/2026-02-10/bd4c532d-5323-41c4-9e58-d6ffe9039d90.png"
              alt="Forest"
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-900/80 to-transparent flex items-center">
              <div className="p-8">
                <h1 className="text-4xl font-bold text-white mb-2">Votre Forêt</h1>
                <p className="text-emerald-100 text-lg">Chaque arbre compte pour la planète</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-emerald-500 to-green-600 text-white">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="p-4 bg-white/20 rounded-full">
                <TreePine className="h-10 w-10" />
              </div>
              <div>
                <p className="text-emerald-100">Total arbres plantés</p>
                <p className="text-4xl font-bold">{totalTrees}</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-green-500 to-teal-600 text-white">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="p-4 bg-white/20 rounded-full">
                <Globe className="h-10 w-10" />
              </div>
              <div>
                <p className="text-green-100">CO₂ compensé</p>
                <p className="text-4xl font-bold">{totalOffset.toFixed(0)} kg</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/80 backdrop-blur border-emerald-200">
            <CardContent className="p-6">
              <p className="text-emerald-600 mb-2">Plantez un nouvel arbre</p>
              <Button 
                onClick={handlePlantTree}
                className="w-full bg-emerald-500 hover:bg-emerald-600"
              >
                <Sprout className="h-5 w-5 mr-2" />
                Planter maintenant
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Plantations List */}
        <Card className="bg-white/80 backdrop-blur border-emerald-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-emerald-900">
              <Award className="h-5 w-5" />
              Historique des plantations
            </CardTitle>
            <CardDescription className="text-emerald-600">
              Tous vos arbres plantés et leurs certificats
            </CardDescription>
          </CardHeader>
          <CardContent>
            {plantations.length === 0 ? (
              <div className="text-center py-12">
                <div className="mx-auto mb-4 p-4 bg-emerald-100 rounded-full w-fit">
                  <TreePine className="h-12 w-12 text-emerald-600" />
                </div>
                <h3 className="text-xl font-semibold text-emerald-900 mb-2">Aucun arbre planté</h3>
                <p className="text-emerald-600 mb-4">Commencez à planter des arbres pour compenser votre empreinte carbone!</p>
                <Button onClick={handlePlantTree} className="bg-emerald-500 hover:bg-emerald-600">
                  <Sprout className="h-4 w-4 mr-2" />
                  Planter mon premier arbre
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {plantations.map((plantation) => (
                  <div 
                    key={plantation.id}
                    className="flex items-center gap-4 p-4 bg-emerald-50 rounded-xl hover:bg-emerald-100 transition-colors"
                  >
                    <div className="p-3 bg-emerald-200 rounded-full">
                      <TreePine className="h-6 w-6 text-emerald-700" />
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-emerald-900">{plantation.tree_species}</span>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          locationColors[plantation.location] || 'bg-gray-100 text-gray-700'
                        }`}>
                          <MapPin className="h-3 w-3 inline mr-1" />
                          {plantation.location}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-emerald-600">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {new Date(plantation.plantation_date).toLocaleDateString('fr-FR')}
                        </span>
                        <span className="flex items-center gap-1">
                          <Globe className="h-4 w-4" />
                          {plantation.carbon_offset} kg CO₂/an
                        </span>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-xs text-emerald-500">Certificat</p>
                      <p className="font-mono text-sm text-emerald-700">{plantation.certificate_id}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Impact Info */}
        <Card className="bg-emerald-50 border-emerald-200 mt-8">
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-emerald-900 mb-4">💡 Le saviez-vous?</h3>
            <div className="grid md:grid-cols-3 gap-4 text-emerald-700">
              <div className="p-4 bg-white rounded-lg">
                <p className="font-bold text-2xl text-emerald-600 mb-1">21 kg</p>
                <p className="text-sm">CO₂ absorbé par arbre/an</p>
              </div>
              <div className="p-4 bg-white rounded-lg">
                <p className="font-bold text-2xl text-emerald-600 mb-1">40 ans</p>
                <p className="text-sm">Durée de vie moyenne d'un arbre</p>
              </div>
              <div className="p-4 bg-white rounded-lg">
                <p className="font-bold text-2xl text-emerald-600 mb-1">840 kg</p>
                <p className="text-sm">CO₂ total absorbé sur sa vie</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}