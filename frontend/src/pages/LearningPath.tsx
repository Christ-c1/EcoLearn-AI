import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { 
  Leaf, ArrowLeft, Clock, CheckCircle2, Circle, 
  Play, Loader2, BookOpen, Lightbulb, HelpCircle
} from 'lucide-react';
import { api, LearningPath as LearningPathType } from '@/lib/api';

interface Module {
  id: number;
  title: string;
  duration_minutes: number;
  content: {
    introduction: string;
    key_concepts: string[];
    detailed_content: string;
    practical_tips: string[];
    quiz: Array<{
      question: string;
      options: string[];
      correct_answer: number;
    }>;
  };
}

export default function LearningPath() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [learningPath, setLearningPath] = useState<LearningPathType | null>(null);
  const [modules, setModules] = useState<Module[]>([]);
  const [currentModuleIndex, setCurrentModuleIndex] = useState(0);
  const [isStudying, setIsStudying] = useState(false);
  const [studyStartTime, setStudyStartTime] = useState<Date | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<Record<number, number>>({});
  const [showQuizResults, setShowQuizResults] = useState(false);

  useEffect(() => {
    checkAuthAndLoad();
  }, [id]);

  const checkAuthAndLoad = async () => {
    try {
      const user = await api.verifyAuth();
      if (!user) {
        navigate('/login');
        return;
      }
      await loadLearningPath();
    } catch {
      navigate('/login');
    }
  };

  const loadLearningPath = async () => {
    try {
      const response = await api.getLearningPath(Number(id));
      if (response) {
        setLearningPath(response);
        const content = JSON.parse(response.content || '{}');
        setModules(content.modules || []);
        setCurrentModuleIndex(response.completed_sessions || 0);
      }
    } catch (error) {
      console.error('Error loading learning path:', error);
      toast({
        title: "Erreur",
        description: "Impossible de charger le parcours",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const startStudying = () => {
    setIsStudying(true);
    setStudyStartTime(new Date());
    setQuizAnswers({});
    setShowQuizResults(false);
  };

  const completeModule = async () => {
    if (!studyStartTime || !learningPath) return;

    const durationMinutes = Math.max(1, Math.round((new Date().getTime() - studyStartTime.getTime()) / 60000));
    
    try {
      // Record session
      await api.recordSession(learningPath.id, durationMinutes, 'laptop');
      
      // Update learning path progress
      const newCompletedSessions = (learningPath.completed_sessions || 0) + 1;
      const newProgress = Math.round((newCompletedSessions / (learningPath.total_sessions || 1)) * 100);
      
      await api.updateLearningPath(learningPath.id, {
        completed_sessions: newCompletedSessions,
        progress: newProgress
      });

      toast({
        title: "Module terminé! 🎉",
        description: `Session de ${durationMinutes} min enregistrée. Empreinte carbone calculée.`
      });

      setIsStudying(false);
      setStudyStartTime(null);
      
      if (currentModuleIndex < modules.length - 1) {
        setCurrentModuleIndex(currentModuleIndex + 1);
      }
      
      await loadLearningPath();
    } catch (error) {
      toast({
        title: "Erreur",
        description: "Impossible d'enregistrer la session",
        variant: "destructive"
      });
    }
  };

  const checkQuiz = () => {
    setShowQuizResults(true);
    const currentModule = modules[currentModuleIndex];
    const quiz = currentModule?.content?.quiz || [];
    const correctAnswers = quiz.filter((q, i) => quizAnswers[i] === q.correct_answer).length;
    
    if (correctAnswers === quiz.length && quiz.length > 0) {
      toast({
        title: "Parfait! 🌟",
        description: "Toutes les réponses sont correctes!"
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

  if (!learningPath || modules.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100 flex items-center justify-center">
        <Card className="bg-white/80 backdrop-blur">
          <CardContent className="p-8 text-center">
            <p className="text-emerald-600">Parcours non trouvé</p>
            <Button onClick={() => navigate('/dashboard')} className="mt-4">
              Retour au dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentModule = modules[currentModuleIndex];
  const progress = learningPath.progress || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-emerald-200 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
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
            <span className="font-semibold text-emerald-800">EcoLearn AI</span>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Path Overview */}
        <Card className="bg-white/80 backdrop-blur border-emerald-200 mb-6">
          <CardHeader>
            <CardTitle className="text-2xl text-emerald-900">{learningPath.title}</CardTitle>
            <CardDescription className="text-emerald-600">{learningPath.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-emerald-600">Progression globale</span>
              <span className="font-medium text-emerald-900">{progress}%</span>
            </div>
            <Progress value={progress} className="h-3 bg-emerald-100" />
          </CardContent>
        </Card>

        {/* Modules List */}
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          {modules.map((module, index) => (
            <Card 
              key={module.id}
              className={`cursor-pointer transition-all ${
                index === currentModuleIndex 
                  ? 'bg-emerald-500 text-white border-emerald-600' 
                  : index < currentModuleIndex
                  ? 'bg-emerald-100 border-emerald-300'
                  : 'bg-white/80 border-emerald-200'
              }`}
              onClick={() => !isStudying && setCurrentModuleIndex(index)}
            >
              <CardContent className="p-4 flex items-center gap-3">
                {index < currentModuleIndex ? (
                  <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                ) : index === currentModuleIndex ? (
                  <Play className="h-5 w-5" />
                ) : (
                  <Circle className="h-5 w-5 text-emerald-300" />
                )}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium truncate ${
                    index === currentModuleIndex ? 'text-white' : 'text-emerald-900'
                  }`}>
                    Module {index + 1}
                  </p>
                  <p className={`text-xs truncate ${
                    index === currentModuleIndex ? 'text-emerald-100' : 'text-emerald-600'
                  }`}>
                    {module.duration_minutes} min
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Current Module Content */}
        {currentModule && (
          <div className="space-y-6">
            <Card className="bg-white/80 backdrop-blur border-emerald-200">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-emerald-100 rounded-lg">
                      <BookOpen className="h-6 w-6 text-emerald-600" />
                    </div>
                    <div>
                      <CardTitle className="text-xl text-emerald-900">{currentModule.title}</CardTitle>
                      <CardDescription className="flex items-center gap-2 text-emerald-600">
                        <Clock className="h-4 w-4" />
                        {currentModule.duration_minutes} minutes
                      </CardDescription>
                    </div>
                  </div>
                  {!isStudying ? (
                    <Button onClick={startStudying} className="bg-emerald-500 hover:bg-emerald-600">
                      <Play className="h-4 w-4 mr-2" />
                      Commencer
                    </Button>
                  ) : (
                    <Button onClick={completeModule} className="bg-green-500 hover:bg-green-600">
                      <CheckCircle2 className="h-4 w-4 mr-2" />
                      Terminer
                    </Button>
                  )}
                </div>
              </CardHeader>
            </Card>

            {isStudying && (
              <>
                {/* Introduction */}
                <Card className="bg-white/80 backdrop-blur border-emerald-200">
                  <CardHeader>
                    <CardTitle className="text-lg text-emerald-900 flex items-center gap-2">
                      <Lightbulb className="h-5 w-5 text-amber-500" />
                      Introduction
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-emerald-700 leading-relaxed">
                      {currentModule.content?.introduction}
                    </p>
                  </CardContent>
                </Card>

                {/* Key Concepts */}
                <Card className="bg-white/80 backdrop-blur border-emerald-200">
                  <CardHeader>
                    <CardTitle className="text-lg text-emerald-900">Concepts clés</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {currentModule.content?.key_concepts?.map((concept, i) => (
                        <span 
                          key={i}
                          className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm"
                        >
                          {concept}
                        </span>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Detailed Content */}
                <Card className="bg-white/80 backdrop-blur border-emerald-200">
                  <CardHeader>
                    <CardTitle className="text-lg text-emerald-900">Contenu détaillé</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-emerald-700 leading-relaxed whitespace-pre-line">
                      {currentModule.content?.detailed_content}
                    </p>
                  </CardContent>
                </Card>

                {/* Practical Tips */}
                {currentModule.content?.practical_tips?.length > 0 && (
                  <Card className="bg-emerald-50 border-emerald-200">
                    <CardHeader>
                      <CardTitle className="text-lg text-emerald-900">💡 Conseils pratiques</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {currentModule.content.practical_tips.map((tip, i) => (
                          <li key={i} className="flex items-start gap-2 text-emerald-700">
                            <Leaf className="h-5 w-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                            {tip}
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Quiz */}
                {currentModule.content?.quiz?.length > 0 && (
                  <Card className="bg-white/80 backdrop-blur border-emerald-200">
                    <CardHeader>
                      <CardTitle className="text-lg text-emerald-900 flex items-center gap-2">
                        <HelpCircle className="h-5 w-5 text-blue-500" />
                        Quiz
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {currentModule.content.quiz.map((q, qIndex) => (
                        <div key={qIndex} className="space-y-3">
                          <p className="font-medium text-emerald-900">{qIndex + 1}. {q.question}</p>
                          <RadioGroup
                            value={String(quizAnswers[qIndex] ?? '')}
                            onValueChange={(value) => setQuizAnswers({...quizAnswers, [qIndex]: Number(value)})}
                          >
                            {q.options.map((option, oIndex) => (
                              <div key={oIndex} className="flex items-center space-x-2">
                                <RadioGroupItem 
                                  value={String(oIndex)} 
                                  id={`q${qIndex}-o${oIndex}`}
                                  className={showQuizResults ? (
                                    oIndex === q.correct_answer 
                                      ? 'border-green-500 text-green-500' 
                                      : quizAnswers[qIndex] === oIndex 
                                      ? 'border-red-500 text-red-500' 
                                      : ''
                                  ) : ''}
                                />
                                <Label 
                                  htmlFor={`q${qIndex}-o${oIndex}`}
                                  className={showQuizResults ? (
                                    oIndex === q.correct_answer 
                                      ? 'text-green-600 font-medium' 
                                      : quizAnswers[qIndex] === oIndex 
                                      ? 'text-red-600' 
                                      : 'text-emerald-700'
                                  ) : 'text-emerald-700'}
                                >
                                  {option}
                                </Label>
                              </div>
                            ))}
                          </RadioGroup>
                        </div>
                      ))}
                      <Button 
                        onClick={checkQuiz}
                        className="bg-blue-500 hover:bg-blue-600"
                        disabled={Object.keys(quizAnswers).length < currentModule.content.quiz.length}
                      >
                        Vérifier les réponses
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}