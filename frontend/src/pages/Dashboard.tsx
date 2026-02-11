import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
import { 
  Leaf, TreePine, BookOpen, Clock, Zap, Award, 
  Plus, Play, BarChart3, LogOut, Loader2, User
} from 'lucide-react';
import { api, LearningPath, UserStats } from '@/lib/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState<{ id: number; email: string; name?: string | null } | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [newTopic, setNewTopic] = useState('');
  const [difficulty, setDifficulty] = useState('beginner');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const userData = await api.verifyAuth();
      if (userData) {
        setUser(userData);
        await loadData();
      } else {
        navigate('/login');
      }
    } catch {
      navigate('/login');
    } finally {
      setIsLoading(false);
    }
  };

  const loadData = async () => {
    try {
      const [pathsRes, statsRes] = await Promise.all([
        api.getLearningPaths(),
        api.getUserStats()
      ]);
      
      if (pathsRes?.items) {
        setLearningPaths(pathsRes.items);
      }
      
      if (statsRes?.items?.[0]) {
        setUserStats(statsRes.items[0]);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleGeneratePath = async () => {
    if (!newTopic.trim()) {
      toast({
        title: "Erreur",
        description: "Veuillez entrer un sujet",
        variant: "destructive"
      });
      return;
    }

    setIsGenerating(true);
    try {
      const response = await api.generateLearningPath(newTopic, difficulty);
      if (response?.success) {
        toast({
          title: "Parcours créé! 🎉",
          description: `Votre parcours "${response.content && typeof response.content === 'object' && 'title' in response.content ? response.content.title : newTopic}" est prêt`
        });
        setNewTopic('');
        await loadData();
      }
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible de générer le parcours",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleLogout = async () => {
    await api.logout();
    navigate('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-emerald-600" />
      </div>
    );
  }

  const stats = userStats || {
    total_learning_time: 0,
    total_carbon_footprint: 0,
    total_trees_planted: 0,
    level: 1,
    experience_points: 0,
    current_streak: 0
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-xl border-b border-emerald-100 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img 
              src="https://mgx-backend-cdn.metadl.com/generate/images/963879/2026-02-10/0455bb53-f1f1-4c3d-ab17-2bdfc205de32.png" 
              alt="EcoLearn AI" 
              className="h-10 w-10 rounded-xl object-cover shadow-md"
            />
            <span className="text-2xl font-bold text-emerald-800">EcoLearn AI</span>
          </div>
          
          <nav className="flex items-center gap-3">
            <Button 
              variant="ghost" 
              className="text-emerald-700 hover:text-emerald-900 hover:bg-emerald-100 rounded-xl"
              onClick={() => navigate('/carbon')}
            >
              <BarChart3 className="h-5 w-5 mr-2" />
              Carbone
            </Button>
            <Button 
              variant="ghost" 
              className="text-emerald-700 hover:text-emerald-900 hover:bg-emerald-100 rounded-xl"
              onClick={() => navigate('/trees')}
            >
              <TreePine className="h-5 w-5 mr-2" />
              Arbres
            </Button>
            <div className="flex items-center gap-2 px-4 py-2 bg-emerald-100 rounded-full">
              <User className="h-5 w-5 text-emerald-600" />
              <span className="text-sm font-medium text-emerald-700 hidden sm:inline">
                {user?.name || user?.email?.split('@')[0]}
              </span>
            </div>
            <Button 
              variant="ghost" 
              size="icon"
              className="text-emerald-700 hover:text-red-600 hover:bg-red-50 rounded-xl"
              onClick={handleLogout}
            >
              <LogOut className="h-5 w-5" />
            </Button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="bg-white/80 backdrop-blur-xl border-emerald-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-5 flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-emerald-400 to-green-500 rounded-xl shadow-md">
                <Clock className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-emerald-600">Temps d'apprentissage</p>
                <p className="text-2xl font-bold text-emerald-900">{stats.total_learning_time || 0} min</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/80 backdrop-blur-xl border-emerald-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-5 flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl shadow-md">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-emerald-600">CO₂ émis</p>
                <p className="text-2xl font-bold text-emerald-900">{((stats.total_carbon_footprint || 0) * 1000).toFixed(0)}g</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/80 backdrop-blur-xl border-emerald-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-5 flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-green-400 to-teal-500 rounded-xl shadow-md">
                <TreePine className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-emerald-600">Arbres plantés</p>
                <p className="text-2xl font-bold text-emerald-900">{stats.total_trees_planted || 0}</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/80 backdrop-blur-xl border-emerald-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-5 flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-purple-400 to-indigo-500 rounded-xl shadow-md">
                <Award className="h-6 w-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-emerald-600">Niveau</p>
                <p className="text-2xl font-bold text-emerald-900">{stats.level || 1}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* XP Progress */}
        <Card className="bg-white/80 backdrop-blur-xl border-emerald-100 rounded-2xl shadow-sm mb-8">
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-semibold text-emerald-700">Progression niveau {stats.level || 1}</span>
              <span className="text-sm text-emerald-600">{stats.experience_points || 0} / {((stats.level || 1) * 1000)} XP</span>
            </div>
            <Progress 
              value={((stats.experience_points || 0) / ((stats.level || 1) * 1000)) * 100} 
              className="h-3 bg-emerald-100"
            />
          </CardContent>
        </Card>

        {/* Create New Path */}
        <Card className="bg-gradient-to-r from-emerald-500 via-green-500 to-teal-500 text-white mb-8 rounded-2xl shadow-xl overflow-hidden">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yIDItNCAyLTRzLTItMi00LTJjMCAwLTItMi0yLTRzMi00IDItNCAyIDIgNCAyYzAgMCAyIDIgMiA0cy0yIDQtMiA0LTIgMi00IDJjMCAwLTIgMi0yIDRzMiA0IDIgNCAyLTIgNC0yYzAgMCAyLTIgMi00eiIvPjwvZz48L2c+PC9zdmc+')] opacity-20"></div>
          <CardHeader className="relative">
            <CardTitle className="flex items-center gap-2 text-xl">
              <Plus className="h-6 w-6" />
              Créer un nouveau parcours d'apprentissage
            </CardTitle>
            <CardDescription className="text-emerald-100">
              L'IA générera un parcours personnalisé sur le sujet de votre choix
            </CardDescription>
          </CardHeader>
          <CardContent className="relative">
            <div className="flex flex-col sm:flex-row gap-4">
              <Input
                placeholder="Ex: Recyclage, Énergie solaire, Biodiversité..."
                value={newTopic}
                onChange={(e) => setNewTopic(e.target.value)}
                className="flex-1 bg-white/20 border-white/30 text-white placeholder:text-emerald-200 rounded-xl h-12"
              />
              <Select value={difficulty} onValueChange={setDifficulty}>
                <SelectTrigger className="w-full sm:w-44 bg-white/20 border-white/30 text-white rounded-xl h-12">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="beginner">Débutant</SelectItem>
                  <SelectItem value="intermediate">Intermédiaire</SelectItem>
                  <SelectItem value="advanced">Avancé</SelectItem>
                </SelectContent>
              </Select>
              <Button 
                onClick={handleGeneratePath}
                disabled={isGenerating}
                className="bg-white text-emerald-600 hover:bg-emerald-50 rounded-xl h-12 px-6 font-semibold shadow-lg"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Génération...
                  </>
                ) : (
                  <>
                    <Leaf className="mr-2 h-5 w-5" />
                    Générer
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Learning Paths */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-emerald-900 flex items-center gap-2">
            <BookOpen className="h-6 w-6" />
            Mes parcours d'apprentissage
          </h2>
          
          {learningPaths.length === 0 ? (
            <Card className="bg-white/80 backdrop-blur-xl border-emerald-100 rounded-2xl">
              <CardContent className="p-12 text-center">
                <div className="mx-auto mb-4 p-4 bg-emerald-100 rounded-full w-fit">
                  <BookOpen className="h-12 w-12 text-emerald-600" />
                </div>
                <h3 className="text-xl font-semibold text-emerald-900 mb-2">Aucun parcours</h3>
                <p className="text-emerald-600">Créez votre premier parcours d'apprentissage écologique!</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {learningPaths.map((path) => (
                <Card 
                  key={path.id} 
                  className="bg-white/80 backdrop-blur-xl border-emerald-100 rounded-2xl hover:shadow-lg transition-all cursor-pointer group"
                  onClick={() => navigate(`/learning/${path.id}`)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <div className="p-2 bg-emerald-100 rounded-xl group-hover:bg-emerald-200 transition-colors">
                        <BookOpen className="h-5 w-5 text-emerald-600" />
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        path.difficulty === 'beginner' ? 'bg-green-100 text-green-700' :
                        path.difficulty === 'intermediate' ? 'bg-amber-100 text-amber-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {path.difficulty === 'beginner' ? 'Débutant' :
                         path.difficulty === 'intermediate' ? 'Intermédiaire' : 'Avancé'}
                      </span>
                    </div>
                    <CardTitle className="text-lg text-emerald-900 mt-3">{path.title}</CardTitle>
                    <CardDescription className="text-emerald-600 line-clamp-2">
                      {path.description || `Parcours sur ${path.topic}`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-emerald-600">Progression</span>
                        <span className="font-semibold text-emerald-900">{path.progress || 0}%</span>
                      </div>
                      <Progress value={path.progress || 0} className="h-2 bg-emerald-100" />
                      <div className="flex items-center justify-between text-sm text-emerald-600">
                        <span>{path.completed_sessions || 0}/{path.total_sessions || 0} modules</span>
                        <Button size="sm" className="bg-emerald-500 hover:bg-emerald-600 rounded-lg">
                          <Play className="h-4 w-4 mr-1" />
                          Continuer
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}