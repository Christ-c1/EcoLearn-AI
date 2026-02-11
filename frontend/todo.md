# EcoLearn AI - Plateforme d'apprentissage écologique

## Design Guidelines

### Design References
- **Duolingo**: Interface gamifiée, progression visuelle
- **Ecosia**: Thème écologique, compteur d'arbres
- **Style**: Modern Eco-Friendly + Gamification + Data Visualization

### Color Palette
- Primary: #10B981 (Emerald Green - nature/growth)
- Secondary: #059669 (Dark Emerald - accents)
- Accent: #34D399 (Light Green - highlights)
- Background: #F0FDF4 (Mint White - light eco feel)
- Dark: #064E3B (Forest Green - text/headers)
- Warning: #F59E0B (Amber - carbon alerts)
- Info: #3B82F6 (Blue - learning progress)

### Typography
- Heading1: Inter font-weight 700 (36px)
- Heading2: Inter font-weight 600 (28px)
- Heading3: Inter font-weight 600 (20px)
- Body: Inter font-weight 400 (16px)
- Small: Inter font-weight 400 (14px)

### Key Component Styles
- **Buttons**: Green gradient (#10B981 to #059669), white text, 8px rounded, hover: brighten
- **Cards**: White background, subtle green border, 12px rounded, shadow-sm
- **Progress Bars**: Green gradient with animation
- **Charts**: D3.js with eco color scheme

### Layout & Spacing
- Dashboard: Sidebar navigation + main content area
- Cards: 16px padding, 24px gaps
- Section padding: 32px vertical

### Images to Generate
1. **hero-forest-learning.jpg** - Beautiful forest scene with sunlight, representing growth and learning (Style: photorealistic, vibrant)
2. **icon-tree-planting.png** - Stylized tree being planted, eco-friendly icon (Style: minimalist illustration)
3. **bg-leaves-pattern.jpg** - Subtle green leaves pattern for backgrounds (Style: soft, abstract)
4. **illustration-carbon-footprint.png** - Visual representation of carbon footprint with earth (Style: modern illustration)

---

## Development Tasks

### 1. Database Setup ✅
- [x] learning_paths table
- [x] carbon_metrics table
- [x] tree_plantations table
- [x] user_stats table

### 2. Frontend Structure
- [ ] App.tsx - Main routing with auth
- [ ] AuthCallback.tsx - OAuth callback handler
- [ ] Login.tsx - Login/Register page
- [ ] Dashboard.tsx - Main dashboard
- [ ] LearningPath.tsx - Learning path detail
- [ ] CarbonTracker.tsx - Carbon metrics visualization
- [ ] TreePlantations.tsx - Tree planting history

### 3. Components
- [ ] Header.tsx - Navigation header
- [ ] Sidebar.tsx - Dashboard sidebar
- [ ] StatsCard.tsx - Statistics display card
- [ ] CarbonChart.tsx - D3.js carbon visualization
- [ ] TreeCounter.tsx - Tree planting counter
- [ ] LearningProgress.tsx - Progress visualization

### 4. Backend Services
- [ ] AI content generation endpoint
- [ ] Carbon calculation service

### 5. Docker Configuration
- [ ] Dockerfile for frontend
- [ ] Dockerfile for backend
- [ ] docker-compose.yml