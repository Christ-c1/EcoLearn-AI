import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { Leaf, TreePine, Sparkles, BookOpen, Loader2, Mail, Lock, User } from 'lucide-react';
import { api } from '@/lib/api';

export default function Login() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Login form
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  
  // Register form
  const [registerName, setRegisterName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerConfirmPassword, setRegisterConfirmPassword] = useState('');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const user = await api.verifyAuth();
      if (user) {
        navigate('/dashboard');
      }
    } catch {
      // Not authenticated
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!loginEmail || !loginPassword) {
      toast({
        title: "Erreur",
        description: "Veuillez remplir tous les champs",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await api.login(loginEmail, loginPassword);
      toast({
        title: "Connexion réussie! 🎉",
        description: "Bienvenue sur EcoLearn AI"
      });
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: "Erreur de connexion",
        description: error instanceof Error ? error.message : "Email ou mot de passe incorrect",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!registerEmail || !registerPassword || !registerConfirmPassword) {
      toast({
        title: "Erreur",
        description: "Veuillez remplir tous les champs obligatoires",
        variant: "destructive"
      });
      return;
    }

    if (registerPassword !== registerConfirmPassword) {
      toast({
        title: "Erreur",
        description: "Les mots de passe ne correspondent pas",
        variant: "destructive"
      });
      return;
    }

    if (registerPassword.length < 6) {
      toast({
        title: "Erreur",
        description: "Le mot de passe doit contenir au moins 6 caractères",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await api.register(registerEmail, registerPassword, registerName);
      toast({
        title: "Inscription réussie! 🎉",
        description: "Bienvenue sur EcoLearn AI"
      });
      navigate('/dashboard');
    } catch (error) {
      toast({
        title: "Erreur d'inscription",
        description: error instanceof Error ? error.message : "Impossible de créer le compte",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-emerald-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-20 left-20 w-64 h-64 bg-emerald-500 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-teal-500 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 w-72 h-72 bg-green-500 rounded-full blur-3xl"></div>
      </div>
      
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="p-6">
          <div className="flex items-center gap-3">
            <img 
              src="https://mgx-backend-cdn.metadl.com/generate/images/963879/2026-02-10/ab3f7b89-dd10-496d-99b4-0326d53b66eb.png" 
              alt="EcoLearn AI" 
              className="h-12 w-12 rounded-xl object-cover shadow-lg"
            />
            <span className="text-2xl font-bold text-emerald-800">EcoLearn AI</span>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="max-w-6xl w-full grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Side - Hero */}
            <div className="space-y-6 hidden lg:block">
              <h1 className="text-5xl font-bold text-emerald-900 leading-tight">
                Apprenez pour la planète
              </h1>
              <p className="text-xl text-emerald-700 leading-relaxed">
                Une plateforme d'apprentissage écologique alimentée par l'IA qui calcule votre empreinte carbone et finance la plantation d'arbres.
              </p>
              
              <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="flex items-center gap-3 bg-white/70 backdrop-blur p-4 rounded-2xl shadow-sm border border-emerald-100">
                  <div className="p-3 bg-gradient-to-br from-emerald-400 to-green-500 rounded-xl shadow-md">
                    <Sparkles className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-emerald-900">IA Adaptative</p>
                    <p className="text-sm text-emerald-600">Contenu personnalisé</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 bg-white/70 backdrop-blur p-4 rounded-2xl shadow-sm border border-emerald-100">
                  <div className="p-3 bg-gradient-to-br from-green-400 to-teal-500 rounded-xl shadow-md">
                    <TreePine className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-emerald-900">Plantation</p>
                    <p className="text-sm text-emerald-600">Arbres réels plantés</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 bg-white/70 backdrop-blur p-4 rounded-2xl shadow-sm border border-emerald-100">
                  <div className="p-3 bg-gradient-to-br from-teal-400 to-cyan-500 rounded-xl shadow-md">
                    <BookOpen className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-emerald-900">Parcours</p>
                    <p className="text-sm text-emerald-600">Apprentissage structuré</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 bg-white/70 backdrop-blur p-4 rounded-2xl shadow-sm border border-emerald-100">
                  <div className="p-3 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl shadow-md">
                    <Leaf className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-emerald-900">Carbone</p>
                    <p className="text-sm text-emerald-600">Suivi en temps réel</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Side - Auth Card */}
            <Card className="bg-white/90 backdrop-blur-xl border-emerald-100 shadow-2xl rounded-3xl">
              <CardHeader className="text-center pb-2">
                <div className="mx-auto mb-4">
                  <img 
                    src="https://mgx-backend-cdn.metadl.com/generate/images/963879/2026-02-10/444e3594-2c80-46c1-94e6-839ba90d1bf5.png" 
                    alt="EcoLearn" 
                    className="h-20 w-20 rounded-2xl object-cover shadow-lg mx-auto"
                  />
                </div>
                <CardTitle className="text-2xl text-emerald-900">Bienvenue sur EcoLearn AI</CardTitle>
                <CardDescription className="text-emerald-600">
                  Connectez-vous ou créez un compte pour commencer
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <Tabs defaultValue="login" className="w-full">
                  <TabsList className="grid w-full grid-cols-2 mb-6 bg-emerald-50 p-1 rounded-xl">
                    <TabsTrigger value="login" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">
                      Connexion
                    </TabsTrigger>
                    <TabsTrigger value="register" className="rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-sm">
                      Inscription
                    </TabsTrigger>
                  </TabsList>
                  
                  {/* Login Tab */}
                  <TabsContent value="login">
                    <form onSubmit={handleLogin} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="login-email" className="text-emerald-800">Email</Label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-3 h-4 w-4 text-emerald-500" />
                          <Input
                            id="login-email"
                            type="email"
                            placeholder="votre@email.com"
                            value={loginEmail}
                            onChange={(e) => setLoginEmail(e.target.value)}
                            className="pl-10 border-emerald-200 focus:border-emerald-500 rounded-xl"
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="login-password" className="text-emerald-800">Mot de passe</Label>
                        <div className="relative">
                          <Lock className="absolute left-3 top-3 h-4 w-4 text-emerald-500" />
                          <Input
                            id="login-password"
                            type="password"
                            placeholder="••••••••"
                            value={loginPassword}
                            onChange={(e) => setLoginPassword(e.target.value)}
                            className="pl-10 border-emerald-200 focus:border-emerald-500 rounded-xl"
                          />
                        </div>
                      </div>
                      
                      <Button 
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 rounded-xl h-12 text-base font-semibold shadow-lg shadow-emerald-500/30"
                      >
                        {isSubmitting ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Connexion...
                          </>
                        ) : (
                          <>
                            <Leaf className="mr-2 h-5 w-5" />
                            Se connecter
                          </>
                        )}
                      </Button>
                    </form>
                  </TabsContent>
                  
                  {/* Register Tab */}
                  <TabsContent value="register">
                    <form onSubmit={handleRegister} className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="register-name" className="text-emerald-800">Nom (optionnel)</Label>
                        <div className="relative">
                          <User className="absolute left-3 top-3 h-4 w-4 text-emerald-500" />
                          <Input
                            id="register-name"
                            type="text"
                            placeholder="Votre nom"
                            value={registerName}
                            onChange={(e) => setRegisterName(e.target.value)}
                            className="pl-10 border-emerald-200 focus:border-emerald-500 rounded-xl"
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="register-email" className="text-emerald-800">Email *</Label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-3 h-4 w-4 text-emerald-500" />
                          <Input
                            id="register-email"
                            type="email"
                            placeholder="votre@email.com"
                            value={registerEmail}
                            onChange={(e) => setRegisterEmail(e.target.value)}
                            className="pl-10 border-emerald-200 focus:border-emerald-500 rounded-xl"
                            required
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="register-password" className="text-emerald-800">Mot de passe *</Label>
                        <div className="relative">
                          <Lock className="absolute left-3 top-3 h-4 w-4 text-emerald-500" />
                          <Input
                            id="register-password"
                            type="password"
                            placeholder="••••••••"
                            value={registerPassword}
                            onChange={(e) => setRegisterPassword(e.target.value)}
                            className="pl-10 border-emerald-200 focus:border-emerald-500 rounded-xl"
                            required
                          />
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="register-confirm" className="text-emerald-800">Confirmer le mot de passe *</Label>
                        <div className="relative">
                          <Lock className="absolute left-3 top-3 h-4 w-4 text-emerald-500" />
                          <Input
                            id="register-confirm"
                            type="password"
                            placeholder="••••••••"
                            value={registerConfirmPassword}
                            onChange={(e) => setRegisterConfirmPassword(e.target.value)}
                            className="pl-10 border-emerald-200 focus:border-emerald-500 rounded-xl"
                            required
                          />
                        </div>
                      </div>
                      
                      <Button 
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 rounded-xl h-12 text-base font-semibold shadow-lg shadow-emerald-500/30"
                      >
                        {isSubmitting ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Inscription...
                          </>
                        ) : (
                          <>
                            <Leaf className="mr-2 h-5 w-5" />
                            S'inscrire
                          </>
                        )}
                      </Button>
                    </form>
                  </TabsContent>
                </Tabs>
                
                <p className="text-center text-sm text-emerald-600 mt-6">
                  🌱 Chaque session = contribution à la reforestation
                </p>
              </CardContent>
            </Card>
          </div>
        </main>

        {/* Footer */}
        <footer className="p-6 text-center text-emerald-600">
          <p>© 2026 EcoLearn AI - Apprendre en préservant la planète</p>
        </footer>
      </div>
    </div>
  );
}