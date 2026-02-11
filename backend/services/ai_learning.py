import logging
import json
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AILearningService:
    """Service for AI-powered learning content generation"""
    
    def __init__(self):
        self.ai_base_url = os.environ.get("APP_AI_BASE_URL")
        self.ai_key = os.environ.get("APP_AI_KEY")
        self.ai_available = bool(self.ai_base_url and self.ai_key)
        logger.info(f"AI Learning Service initialized. AI available: {self.ai_available}")
    
    async def generate_learning_path(
        self,
        topic: str,
        difficulty: str = "beginner",
        language: str = "fr"
    ) -> Dict[str, Any]:
        """Generate a complete learning path"""
        
        # If AI service is available, use it
        if self.ai_available:
            try:
                return await self._generate_with_ai(topic, difficulty, language)
            except Exception as e:
                logger.warning(f"AI generation failed, using fallback: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to static content generation
        return self._generate_static_content(topic, difficulty)
    
    async def _generate_with_ai(
        self,
        topic: str,
        difficulty: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate content using AI Hub service (OpenRouter compatible)"""
        from services.aihub import AIHubService
        from schemas.aihub import GenTxtRequest, ChatMessage
        
        ai_service = AIHubService()
        
        difficulty_descriptions = {
            "beginner": "débutant - concepts de base, explications simples",
            "intermediate": "intermédiaire - concepts approfondis, exercices pratiques",
            "advanced": "avancé - concepts complexes, projets pratiques"
        }
        
        diff_desc = difficulty_descriptions.get(difficulty, difficulty_descriptions["beginner"])
        
        system_prompt = """Tu es un expert en pédagogie environnementale. Tu crées des parcours d'apprentissage structurés et engageants sur des sujets écologiques.
        
Réponds UNIQUEMENT en JSON valide avec cette structure exacte:
{
    "title": "Titre du parcours",
    "description": "Description courte du parcours",
    "modules": [
        {
            "id": 1,
            "title": "Titre du module",
            "duration_minutes": 15,
            "content": {
                "introduction": "Introduction au module",
                "key_concepts": ["concept1", "concept2", "concept3"],
                "detailed_content": "Contenu détaillé du module",
                "practical_tips": ["conseil1", "conseil2"],
                "quiz": [
                    {
                        "question": "Question?",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": 0
                    }
                ]
            }
        }
    ],
    "total_duration_minutes": 60,
    "learning_objectives": ["objectif1", "objectif2", "objectif3"]
}"""

        user_prompt = f"""Crée un parcours d'apprentissage complet sur le sujet: "{topic}"
        
Niveau de difficulté: {diff_desc}
Langue: {language}

Le parcours doit contenir 3-4 modules progressifs avec du contenu éducatif de qualité sur ce sujet écologique.

IMPORTANT: Réponds UNIQUEMENT avec le JSON, sans aucun texte avant ou après."""

        # Use a model available on OpenRouter
        # google/gemini-flash-1.5 is fast and affordable
        request = GenTxtRequest(
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt)
            ],
            model="google/gemini-flash-1.5",  # OpenRouter model name
            temperature=0.7,
            max_tokens=4096
        )
        
        response = await ai_service.gentxt(request)
        content = response.content
        
        logger.info(f"AI response received, length: {len(content)}")
        
        # Try to parse JSON from response
        try:
            # Clean up the response
            content = content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                parts = content.split("```")
                if len(parts) >= 2:
                    content = parts[1]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Response was: {content[:500]}...")
            return self._generate_static_content(topic, difficulty)
    
    def _generate_static_content(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate static learning content without AI"""
        
        # Map topics to predefined content
        topic_lower = topic.lower()
        
        # Default eco-friendly content templates
        templates = {
            "recyclage": {
                "title": "Maîtriser le Recyclage",
                "description": "Apprenez les bonnes pratiques du recyclage pour réduire votre impact environnemental",
                "modules": [
                    {
                        "id": 1,
                        "title": "Les bases du recyclage",
                        "duration_minutes": 15,
                        "content": {
                            "introduction": "Le recyclage est un pilier fondamental de l'économie circulaire. Il permet de transformer nos déchets en nouvelles ressources.",
                            "key_concepts": ["Tri sélectif", "Matériaux recyclables", "Économie circulaire"],
                            "detailed_content": "Le recyclage commence par un tri efficace. Les principaux matériaux recyclables sont le papier, le carton, le verre, le plastique et le métal. Chaque matériau a son propre processus de recyclage.",
                            "practical_tips": ["Rincez vos emballages avant de les jeter", "Aplatissez les cartons pour gagner de la place"],
                            "quiz": [
                                {
                                    "question": "Quel matériau est recyclable à l'infini ?",
                                    "options": ["Plastique", "Verre", "Papier", "Bois"],
                                    "correct_answer": 1
                                }
                            ]
                        }
                    },
                    {
                        "id": 2,
                        "title": "Le tri sélectif en pratique",
                        "duration_minutes": 20,
                        "content": {
                            "introduction": "Maîtriser le tri sélectif est essentiel pour un recyclage efficace.",
                            "key_concepts": ["Poubelle jaune", "Poubelle verte", "Déchets spéciaux"],
                            "detailed_content": "En France, le système de tri utilise différentes couleurs de poubelles. La poubelle jaune accueille les emballages, la verte le verre, et la grise les ordures ménagères.",
                            "practical_tips": ["Consultez le guide de tri de votre commune", "En cas de doute, jetez dans la poubelle grise"],
                            "quiz": [
                                {
                                    "question": "Où jeter une bouteille en plastique ?",
                                    "options": ["Poubelle grise", "Poubelle jaune", "Poubelle verte", "Compost"],
                                    "correct_answer": 1
                                }
                            ]
                        }
                    },
                    {
                        "id": 3,
                        "title": "Réduire ses déchets",
                        "duration_minutes": 15,
                        "content": {
                            "introduction": "Le meilleur déchet est celui qu'on ne produit pas.",
                            "key_concepts": ["Zéro déchet", "Réutilisation", "Compostage"],
                            "detailed_content": "Avant de recycler, pensez à réduire et réutiliser. Privilégiez les produits avec moins d'emballages, utilisez des sacs réutilisables et compostez vos déchets organiques.",
                            "practical_tips": ["Apportez vos propres contenants", "Achetez en vrac quand c'est possible"],
                            "quiz": [
                                {
                                    "question": "Quelle est la première étape de la règle des 3R ?",
                                    "options": ["Recycler", "Réutiliser", "Réduire", "Réparer"],
                                    "correct_answer": 2
                                }
                            ]
                        }
                    }
                ],
                "total_duration_minutes": 50,
                "learning_objectives": [
                    "Comprendre les principes du recyclage",
                    "Maîtriser le tri sélectif",
                    "Adopter des habitudes zéro déchet"
                ]
            },
            "energie": {
                "title": "Économiser l'Énergie au Quotidien",
                "description": "Découvrez comment réduire votre consommation d'énergie et votre empreinte carbone",
                "modules": [
                    {
                        "id": 1,
                        "title": "Comprendre sa consommation",
                        "duration_minutes": 15,
                        "content": {
                            "introduction": "Comprendre d'où vient votre consommation d'énergie est la première étape pour la réduire.",
                            "key_concepts": ["kWh", "Facture énergétique", "Appareils énergivores"],
                            "detailed_content": "Le chauffage représente environ 60% de la consommation d'énergie d'un foyer, suivi par l'eau chaude (20%) et les appareils électriques (20%).",
                            "practical_tips": ["Relevez votre compteur régulièrement", "Identifiez vos appareils les plus gourmands"],
                            "quiz": [
                                {
                                    "question": "Quel poste consomme le plus d'énergie dans un foyer ?",
                                    "options": ["Éclairage", "Chauffage", "Électroménager", "Multimédia"],
                                    "correct_answer": 1
                                }
                            ]
                        }
                    },
                    {
                        "id": 2,
                        "title": "Gestes simples au quotidien",
                        "duration_minutes": 20,
                        "content": {
                            "introduction": "De petits gestes quotidiens peuvent faire une grande différence.",
                            "key_concepts": ["Veille", "Éclairage LED", "Température idéale"],
                            "detailed_content": "Éteindre les appareils en veille, utiliser des ampoules LED, et baisser le chauffage de 1°C peut réduire votre facture de 7%.",
                            "practical_tips": ["Utilisez des multiprises avec interrupteur", "Réglez votre chauffage à 19°C"],
                            "quiz": [
                                {
                                    "question": "De combien baisser le chauffage de 1°C réduit-il la facture ?",
                                    "options": ["3%", "5%", "7%", "10%"],
                                    "correct_answer": 2
                                }
                            ]
                        }
                    }
                ],
                "total_duration_minutes": 35,
                "learning_objectives": [
                    "Analyser sa consommation d'énergie",
                    "Appliquer des éco-gestes efficaces",
                    "Réduire sa facture énergétique"
                ]
            },
            "eau": {
                "title": "Préserver l'Eau Précieuse",
                "description": "Apprenez à économiser l'eau et protéger cette ressource vitale",
                "modules": [
                    {
                        "id": 1,
                        "title": "L'eau, une ressource limitée",
                        "duration_minutes": 15,
                        "content": {
                            "introduction": "L'eau douce ne représente que 2,5% de l'eau sur Terre, et seulement 1% est accessible.",
                            "key_concepts": ["Cycle de l'eau", "Eau potable", "Stress hydrique"],
                            "detailed_content": "Un Français consomme en moyenne 150 litres d'eau par jour. Le réchauffement climatique aggrave les pénuries d'eau dans de nombreuses régions.",
                            "practical_tips": ["Fermez le robinet pendant le brossage des dents", "Préférez les douches aux bains"],
                            "quiz": [
                                {
                                    "question": "Quelle est la consommation moyenne d'eau par jour en France ?",
                                    "options": ["50 litres", "100 litres", "150 litres", "200 litres"],
                                    "correct_answer": 2
                                }
                            ]
                        }
                    },
                    {
                        "id": 2,
                        "title": "Économiser l'eau au quotidien",
                        "duration_minutes": 20,
                        "content": {
                            "introduction": "De nombreux gestes simples permettent de réduire significativement sa consommation d'eau.",
                            "key_concepts": ["Économiseurs d'eau", "Récupération d'eau de pluie", "Arrosage intelligent"],
                            "detailed_content": "Installer des mousseurs sur les robinets peut réduire la consommation de 50%. Récupérer l'eau de pluie permet d'arroser le jardin gratuitement.",
                            "practical_tips": ["Installez un récupérateur d'eau de pluie", "Arrosez le soir pour limiter l'évaporation"],
                            "quiz": [
                                {
                                    "question": "De combien un mousseur peut-il réduire la consommation d'eau ?",
                                    "options": ["10%", "25%", "50%", "75%"],
                                    "correct_answer": 2
                                }
                            ]
                        }
                    }
                ],
                "total_duration_minutes": 35,
                "learning_objectives": [
                    "Comprendre l'importance de l'eau",
                    "Adopter des gestes économes",
                    "Protéger les ressources en eau"
                ]
            },
            "biodiversité": {
                "title": "Protéger la Biodiversité",
                "description": "Découvrez l'importance de la biodiversité et comment la préserver",
                "modules": [
                    {
                        "id": 1,
                        "title": "Qu'est-ce que la biodiversité ?",
                        "duration_minutes": 15,
                        "content": {
                            "introduction": "La biodiversité englobe toutes les formes de vie sur Terre et leurs interactions.",
                            "key_concepts": ["Écosystèmes", "Espèces menacées", "Services écosystémiques"],
                            "detailed_content": "La biodiversité fournit des services essentiels : pollinisation, purification de l'air et de l'eau, régulation du climat. Actuellement, un million d'espèces sont menacées d'extinction.",
                            "practical_tips": ["Plantez des fleurs mellifères", "Évitez les pesticides"],
                            "quiz": [
                                {
                                    "question": "Combien d'espèces sont menacées d'extinction ?",
                                    "options": ["100 000", "500 000", "1 million", "5 millions"],
                                    "correct_answer": 2
                                }
                            ]
                        }
                    },
                    {
                        "id": 2,
                        "title": "Agir pour la biodiversité",
                        "duration_minutes": 20,
                        "content": {
                            "introduction": "Chacun peut contribuer à la protection de la biodiversité à son échelle.",
                            "key_concepts": ["Jardins naturels", "Corridors écologiques", "Consommation responsable"],
                            "detailed_content": "Créer un jardin favorable à la biodiversité, installer des nichoirs, laisser des zones sauvages sont autant d'actions positives.",
                            "practical_tips": ["Installez un hôtel à insectes", "Laissez une partie de votre jardin en friche"],
                            "quiz": [
                                {
                                    "question": "Quel est le rôle des abeilles dans l'écosystème ?",
                                    "options": ["Prédation", "Pollinisation", "Décomposition", "Filtration"],
                                    "correct_answer": 1
                                }
                            ]
                        }
                    }
                ],
                "total_duration_minutes": 35,
                "learning_objectives": [
                    "Comprendre la biodiversité",
                    "Identifier les menaces",
                    "Agir pour la protection"
                ]
            }
        }
        
        # Try to find a matching template
        for key, template in templates.items():
            if key in topic_lower:
                return template
        
        # Generate generic content for unknown topics
        return {
            "title": f"Parcours: {topic}",
            "description": f"Découvrez les fondamentaux de {topic} pour un mode de vie plus durable",
            "modules": [
                {
                    "id": 1,
                    "title": f"Introduction à {topic}",
                    "duration_minutes": 15,
                    "content": {
                        "introduction": f"Bienvenue dans ce module d'introduction sur {topic}. Vous allez découvrir les concepts clés et leur importance pour l'environnement.",
                        "key_concepts": ["Développement durable", "Impact environnemental", "Actions concrètes"],
                        "detailed_content": f"Le sujet de {topic} est essentiel dans notre transition écologique. Comprendre ses enjeux nous permet d'agir de manière plus responsable au quotidien.",
                        "practical_tips": [
                            "Commencez par de petits changements",
                            "Partagez vos connaissances avec votre entourage"
                        ],
                        "quiz": [
                            {
                                "question": f"Pourquoi {topic} est-il important pour l'environnement ?",
                                "options": [
                                    "Pour réduire notre impact",
                                    "Pour économiser de l'argent",
                                    "Les deux réponses",
                                    "Aucune des réponses"
                                ],
                                "correct_answer": 2
                            }
                        ]
                    }
                },
                {
                    "id": 2,
                    "title": "Mettre en pratique",
                    "duration_minutes": 20,
                    "content": {
                        "introduction": "Passons maintenant à la pratique avec des actions concrètes.",
                        "key_concepts": ["Éco-gestes", "Habitudes durables", "Mesure d'impact"],
                        "detailed_content": "Chaque action compte. En adoptant de nouvelles habitudes, vous contribuez à la préservation de notre planète.",
                        "practical_tips": [
                            "Fixez-vous des objectifs réalisables",
                            "Suivez vos progrès régulièrement"
                        ],
                        "quiz": [
                            {
                                "question": "Quelle est la meilleure façon de commencer ?",
                                "options": [
                                    "Tout changer d'un coup",
                                    "Commencer par de petits gestes",
                                    "Attendre d'être parfaitement prêt",
                                    "Ne rien faire"
                                ],
                                "correct_answer": 1
                            }
                        ]
                    }
                }
            ],
            "total_duration_minutes": 35,
            "learning_objectives": [
                f"Comprendre les enjeux de {topic}",
                "Identifier des actions concrètes",
                "Mesurer son impact positif"
            ]
        }


class CarbonCalculatorService:
    """Service for calculating carbon footprint of learning sessions"""
    
    # Average power consumption by device type (in Watts)
    DEVICE_POWER = {
        "desktop": 200,  # Desktop computer
        "laptop": 50,    # Laptop
        "tablet": 10,    # Tablet
        "mobile": 5      # Mobile phone
    }
    
    # Carbon intensity of electricity (gCO2/kWh) - average global
    CARBON_INTENSITY = 475  # grams CO2 per kWh
    
    # CO2 absorbed by one tree per year (kg)
    TREE_CO2_ABSORPTION = 21  # kg CO2 per tree per year
    
    def calculate_session_carbon(
        self,
        duration_minutes: int,
        device_type: str = "laptop"
    ) -> Dict[str, Any]:
        """Calculate carbon footprint for a learning session"""
        
        # Get device power consumption
        power_watts = self.DEVICE_POWER.get(device_type.lower(), self.DEVICE_POWER["laptop"])
        
        # Calculate energy consumed (Wh)
        duration_hours = duration_minutes / 60
        energy_wh = power_watts * duration_hours
        
        # Calculate carbon footprint (grams CO2)
        carbon_grams = (energy_wh / 1000) * self.CARBON_INTENSITY
        
        # Calculate tree contribution (fraction of a tree needed to offset)
        # Convert grams to kg and divide by annual tree absorption
        carbon_kg = carbon_grams / 1000
        trees_contribution = carbon_kg / self.TREE_CO2_ABSORPTION
        
        return {
            "session_duration": duration_minutes,
            "device_type": device_type,
            "energy_consumed_wh": round(energy_wh, 2),
            "carbon_footprint_grams": round(carbon_grams, 2),
            "carbon_footprint_kg": round(carbon_kg, 4),
            "trees_contribution": round(trees_contribution, 6),
            "trees_to_plant": max(1, round(trees_contribution * 100))  # Scale up for meaningful contribution
        }
    
    def get_carbon_stats(
        self,
        total_carbon_kg: float,
        total_trees_planted: int
    ) -> Dict[str, Any]:
        """Get overall carbon statistics"""
        
        # Calculate net carbon impact
        carbon_offset_kg = total_trees_planted * self.TREE_CO2_ABSORPTION
        net_carbon_kg = total_carbon_kg - carbon_offset_kg
        
        return {
            "total_carbon_emitted_kg": round(total_carbon_kg, 2),
            "total_carbon_offset_kg": round(carbon_offset_kg, 2),
            "net_carbon_kg": round(net_carbon_kg, 2),
            "is_carbon_positive": net_carbon_kg <= 0,
            "trees_planted": total_trees_planted,
            "equivalent_car_km": round(total_carbon_kg / 0.12, 1),  # Average car emits 120g/km
            "equivalent_flights_paris_ny": round(total_carbon_kg / 1000, 2)  # ~1 ton CO2 per flight
        }