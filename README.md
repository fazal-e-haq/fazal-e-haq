<!-- Top Animated Banner -->
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://capsule-render.vercel.app/api?type=waving&color=38BDF8&height=250&section=header&text=Fazal-e-Haq&fontSize=70&fontAlignY=38&desc=Flutter%20Developer%20%7C%20UI/UX%20Designer&descSize=22&descAlignY=58&animation=twinkling&theme=dark">
    <source media="(prefers-color-scheme: light)" srcset="https://capsule-render.vercel.app/api?type=waving&color=0284C7&height=250&section=header&text=Fazal-e-Haq&fontSize=70&fontAlignY=38&desc=Flutter%20Developer%20%7C%20UI/UX%20Designer&descSize=22&descAlignY=58&animation=twinkling&fontColor=ffffff">
    <img src="https://capsule-render.vercel.app/api?type=waving&color=38BDF8&height=250&section=header&text=Fazal-e-Haq&fontSize=70&fontAlignY=38&desc=Flutter%20Developer%20%7C%20UI/UX%20Designer&descSize=22&descAlignY=58&animation=twinkling" alt="Header" width="100%" />
  </picture>
</div>



<div align="center">
  <img src="https://komarev.com/ghpvc/?username=fazal-e-haq&label=Profile%20Views&color=0ea5e9&style=flat-square" alt="Profile Views" />
</div>


<h2 align="center"> 👨‍💻 Developer.dart </h2>

```dart
import 'package:flutter/material.dart';

// --- Domain Models ---
abstract class Developer {}
class Idea {}
class Design {}
class App {}
class Success extends App { Success(App app); }

/// Represents a passionate software engineer specializing in mobile and web development.
/// 
/// Combines clean architecture principles with pixel-perfect UI/UX design to 
/// create seamless digital experiences.
class FazalEHaq extends Developer {
  final String name = 'Fazal-e-Haq';
  final String role = 'Flutter Developer & UI/UX Designer';
  
  // --- Core Competencies ---
  final Map<String, List<String>> techStack = const {
    '🚀 Core':             ['Flutter', 'Dart'],
    '🧠 State Mgmt':       ['Provider', 'GetX'],
    '☁️ Backend & DB':   ['Firebase', 'Supabase', 'Isar Database'],
    '🌐 Networking':       ['REST API', 'Postman'],
    '🎨 UI/UX Design':     ['Figma', 'Canva'],
    '🛠️ Tools & IDEs':    ['Git', 'GitHub', 'Android Studio', 'Antigravity'],
  };

  /// Asynchronously builds scalable and highly responsive applications.
  /// 
  /// Takes an [Idea] and a [Design], and returns a production-ready application.
  Future<App> buildApp({required Idea idea, required Design design}) async {
    try {
      // 1. Analyze and plan the architecture
      await _analyzeRequirements(idea);
      
      // 2. Translate Figma designs into pixel-perfect widgets
      final ui = await _craftIntuitiveInterfaces(design);
      
      // 3. Implement robust logic and state management
      final app = await _writeCleanMaintainableCode(ui);
      
      return Success(app);
    } catch (bug) {
      // Squash bugs efficiently 🐛🔨
      return _refactorAndFix(bug);
    }
  }
  
  // Reach out for collaborations, freelance work, or just to chat!
  void contactMe() {
    print('🌐 Portfolio: https://fazal-portfolio.web.app');
    print('🔗 LinkedIn:  https://linkedin.com/in/fazal-e-haq3');
    print('📧 Email:     fazal.e.haq216@gmail.com');
    print('📸 Instagram: https://www.instagram.com/fazalehaq.dev');
  }

  // Private helpers
  Future<void> _analyzeRequirements(Idea idea) async {}
  Future<void> _craftIntuitiveInterfaces(Design design) async {}
  Future<App> _writeCleanMaintainableCode(void ui) async => App();
  App _refactorAndFix(Object bug) => App();
}
```

<br>

<h2 align="center"> 🏆 GitHub Analytics </h2>
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-trophy.vercel.app/?username=fazal-e-haq&theme=radical&no-frame=true&no-bg=true&margin-w=15">
    <source media="(prefers-color-scheme: light)" srcset="https://github-profile-trophy.vercel.app/?username=fazal-e-haq&theme=flat&no-frame=true&no-bg=true&margin-w=15">
    <img src="https://github-profile-trophy.vercel.app/?username=fazal-e-haq&theme=radical&no-frame=true&no-bg=true&margin-w=15" alt="Trophies" />
  </picture>
</div>
<br>
<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api?username=fazal-e-haq&show_icons=true&theme=tokyonight&hide_border=true&bg_color=0D1117">
    <source media="(prefers-color-scheme: light)" srcset="https://github-readme-stats.vercel.app/api?username=fazal-e-haq&show_icons=true&theme=default&hide_border=true&bg_color=ffffff">
    <img src="https://github-readme-stats.vercel.app/api?username=fazal-e-haq&show_icons=true&theme=tokyonight&hide_border=true&bg_color=0D1117" alt="GitHub Stats" />
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api/top-langs/?username=fazal-e-haq&layout=compact&theme=tokyonight&hide_border=true&bg_color=0D1117">
    <source media="(prefers-color-scheme: light)" srcset="https://github-readme-stats.vercel.app/api/top-langs/?username=fazal-e-haq&layout=compact&theme=default&hide_border=true&bg_color=ffffff">
    <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=fazal-e-haq&layout=compact&theme=tokyonight&hide_border=true&bg_color=0D1117" alt="Top Languages" />
  </picture>
</div>
