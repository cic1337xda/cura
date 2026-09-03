import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'widgets/glass_card.dart';
import 'widgets/glass_dock.dart';
import 'widgets/patient_card.dart';

void main() {
  runApp(const CuraApp());
}

class CuraApp extends StatefulWidget {
  const CuraApp({super.key});

  @override
  State<CuraApp> createState() => _CuraAppState();
}

class _CuraAppState extends State<CuraApp> {
  ThemeMode _themeMode = ThemeMode.light;
  int _currentDockIndex = 0;

  void _toggleTheme() {
    setState(() {
      _themeMode = _themeMode == ThemeMode.light ? ThemeMode.dark : ThemeMode.light;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Cura. HMS',
      theme: ThemeData(
        brightness: Brightness.light,
        primaryColor: const Color(0xFF007AFF),
        scaffoldBackgroundColor: const Color(0xFFE0F2FE),
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF0A84FF),
        scaffoldBackgroundColor: const Color(0xFF0F172A),
      ),
      themeMode: _themeMode,
      home: MainDashboardScreen(
        onThemeToggle: _toggleTheme,
        currentDockIndex: _currentDockIndex,
        onDockTap: (index) => setState(() => _currentDockIndex = index),
      ),
    );
  }
}

class PatientCardData {
  final String name;
  final String id;
  PatientCardData({required this.name, required this.id});

  Map<String, dynamic> toJson() => {'name': name, 'id': id};
  factory PatientCardData.fromJson(Map<String, dynamic> json) =>
      PatientCardData(name: json['name'] ?? '', id: json['id'] ?? '');
}

class MainDashboardScreen extends StatefulWidget {
  final VoidCallback onThemeToggle;
  final int currentDockIndex;
  final Function(int) onDockTap;

  const MainDashboardScreen({
    super.key,
    required this.onThemeToggle,
    required this.currentDockIndex,
    required this.onDockTap,
  });

  @override
  State<MainDashboardScreen> createState() => _MainDashboardScreenState();
}

class _MainDashboardScreenState extends State<MainDashboardScreen>
    with TickerProviderStateMixin {
  static const _storageKey = 'cura_cards';
  static const platform = MethodChannel('com.example.cura_app/hce');

  List<PatientCardData> _cards = [];
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    _loadCards();
  }

  Future<void> _loadCards() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_storageKey);
    if (raw != null) {
      final list = jsonDecode(raw) as List;
      setState(() {
        _cards = list.map((e) => PatientCardData.fromJson(e)).toList();
        _loaded = true;
      });
    } else {
      setState(() => _loaded = true);
    }
  }

  Future<void> _saveCards() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = jsonEncode(_cards.map((c) => c.toJson()).toList());
    await prefs.setString(_storageKey, raw);
  }

  void _activateCardEmulation(String patientId) async {
    try {
      await platform.invokeMethod('setPatientId', {'patientId': patientId});
    } on PlatformException catch (e) {
      debugPrint("HCE activation failed: '${e.message}'.");
    }
  }

  void _deactivateCardEmulation() async {
    try {
      await platform.invokeMethod('setPatientId', {'patientId': ''});
    } on PlatformException catch (e) {
      debugPrint("HCE deactivation failed: '${e.message}'.");
    }
  }

  void _openCardsList() {
    if (_cards.isEmpty) {
      _showAddCardSheet(context);
    } else {
      _showCardsSheet(context);
    }
  }

  void _showCardsSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return Container(
          height: MediaQuery.of(context).size.height * 0.7,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.85),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
            border: Border.all(color: Colors.white.withOpacity(0.4), width: 1.5),
          ),
          child: ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
            child: Builder(builder: (ctx) {
              final dm = Theme.of(ctx).brightness == Brightness.dark;
              return Column(
              children: [
                const SizedBox(height: 12),
                Center(
                  child: Container(
                    width: 40, height: 5,
                    decoration: BoxDecoration(
                      color: Colors.black12,
                      borderRadius: BorderRadius.circular(2.5),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  "Your Cards",
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, letterSpacing: -0.5, color: dm ? Colors.white : Colors.black87),
                ),
                const SizedBox(height: 8),
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    itemCount: _cards.length + 1,
                    itemBuilder: (ctx, i) {
                      if (i == _cards.length) {
                        return Padding(
                          padding: const EdgeInsets.only(top: 8, bottom: 24),
                          child: SizedBox(
                            width: double.infinity,
                            height: 48,
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF007AFF),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                              ),
                              onPressed: () {
                                Navigator.pop(ctx);
                                _showAddCardSheet(context);
                              },
                              icon: const Icon(Icons.add_rounded, color: Colors.white),
                              label: const Text("Add New Card", style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                            ),
                          ),
                        );
                      }
                      final card = _cards[i];
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: GestureDetector(
                          onTap: () {
                            Navigator.pop(ctx);
                            _showNfcOverlay(card);
                          },
                          child: Stack(
                            children: [
                              DigitalPatientCard(
                                patientName: card.name,
                                patientId: card.id,
                                hospitalName: "Cura. Hospital",
                              ),
                              Positioned(
                                top: 8, right: 8,
                                child: GestureDetector(
                                  onTap: () async {
                                    setState(() => _cards.removeAt(i));
                                    await _saveCards();
                                    if (_cards.isEmpty) {
                                      Navigator.pop(ctx);
                                    } else {
                                      Navigator.pop(ctx);
                                      _showCardsSheet(context);
                                    }
                                  },
                                  child: Container(
                                    width: 32, height: 32,
                                    decoration: BoxDecoration(
                                      color: Colors.red.withOpacity(0.9),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: const Icon(Icons.delete_rounded, color: Colors.white, size: 18),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            );
          }),
        ),
    );
      },
    );
  }

  void _showAddCardSheet(BuildContext context) {
    final nameCtrl = TextEditingController();
    final idCtrl = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      transitionAnimationController: AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 200),
        reverseDuration: const Duration(milliseconds: 180),
      ),
      builder: (ctx) {
        return AnimatedPadding(
          padding: MediaQuery.of(context).viewInsets,
          duration: const Duration(milliseconds: 100),
          curve: Curves.easeOut,
          child: Container(
            height: MediaQuery.of(context).size.height * 0.55,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.85),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
              border: Border.all(color: Colors.white.withOpacity(0.4), width: 1.5),
            ),
            child: ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
              child: Padding(
                padding: const EdgeInsets.all(28.0),
                child: Builder(builder: (ctx) {
                  final dark = Theme.of(ctx).brightness == Brightness.dark;
                  return SingleChildScrollView(
                    physics: const BouncingScrollPhysics(),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Center(
                          child: Container(
                            width: 40, height: 5,
                            decoration: BoxDecoration(
                              color: Colors.black12,
                              borderRadius: BorderRadius.circular(2.5),
                            ),
                          ),
                        ),
                        const SizedBox(height: 24),
                        Text("Register Patient Card", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: -0.5, color: dark ? Colors.white : const Color(0xFF1C1C1E))),
                        const SizedBox(height: 8),
                        Text("Add a virtual medical card for Host Card Emulation (HCE).", style: TextStyle(fontSize: 13, color: dark ? Colors.white54 : Colors.black45)),
                      const SizedBox(height: 28),
                      _buildField(label: "PATIENT FULL NAME", placeholder: "e.g., Abdullah Afiq", icon: Icons.person_rounded, controller: nameCtrl, isDark: dark),
                      const SizedBox(height: 16),
                      _buildField(label: "HOSPITAL IDENTITY SYSTEM (ID)", placeholder: "e.g., HMS-2026-BMI", icon: Icons.badge_rounded, controller: idCtrl, isDark: dark),
                      const SizedBox(height: 32),
                      SizedBox(
                        width: double.infinity, height: 54,
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF007AFF),
                            elevation: 0,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          ),
                          onPressed: () {
                            if (nameCtrl.text.isNotEmpty && idCtrl.text.isNotEmpty) {
                              setState(() {
                                _cards.add(PatientCardData(name: nameCtrl.text, id: idCtrl.text));
                              });
                              _saveCards();
                              Navigator.pop(ctx);
                            }
                          },
                          child: const Text("Generate Digital Token", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ),
      ));
      },
    );
  }

  Widget _buildField({
    required String label,
    required String placeholder,
    required IconData icon,
    required TextEditingController controller,
    bool isDark = false,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF007AFF), letterSpacing: 1.0)),
        const SizedBox(height: 6),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: isDark ? Colors.white.withOpacity(0.06) : Colors.black.withOpacity(0.04),
            borderRadius: BorderRadius.circular(14),
          ),
          child: TextField(
            controller: controller,
            style: TextStyle(color: isDark ? Colors.white : Colors.black87),
            decoration: InputDecoration(
              icon: Icon(icon, size: 20, color: isDark ? Colors.white38 : Colors.black38),
              hintText: placeholder,
              hintStyle: TextStyle(color: isDark ? Colors.white30 : Colors.black38, fontSize: 14),
              border: InputBorder.none,
            ),
          ),
        ),
      ],
    );
  }

  void _showNfcOverlay(PatientCardData card) {
    _activateCardEmulation(card.id);
    showGeneralDialog(
      context: context,
      barrierDismissible: false,
      pageBuilder: (context, __, ___) {
        return NfcActiveOverlay(
          cardWidget: DigitalPatientCard(
            patientName: card.name,
            patientId: card.id,
            hospitalName: "Cura. Hospital",
          ),
          onClose: () {
            _deactivateCardEmulation();
            Navigator.pop(context);
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      resizeToAvoidBottomInset: false,
      body: Stack(
        children: [
          // Orbs
          Positioned(top: -80, left: -40, child: Container(width: 320, height: 320, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [const Color(0xFF007AFF).withOpacity(0.45), const Color(0xFF007AFF).withOpacity(0.0)])))),
          Positioned(top: 250, right: -90, child: Container(width: 360, height: 360, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [const Color(0xFF30D158).withOpacity(0.25), const Color(0xFF30D158).withOpacity(0.0)])))),
          Positioned(bottom: 150, left: -100, child: Container(width: 400, height: 400, decoration: BoxDecoration(shape: BoxShape.circle, gradient: RadialGradient(colors: [Colors.purple.withOpacity(0.25), Colors.purple.withOpacity(0.0)])))),

          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Cura.', style: TextStyle(fontSize: 34, fontWeight: FontWeight.w900, letterSpacing: -1.5, color: isDarkMode ? Colors.white : const Color(0xFF0F172A))),
                      IconButton(icon: Icon(isDarkMode ? Icons.light_mode_rounded : Icons.dark_mode_rounded), onPressed: widget.onThemeToggle),
                    ],
                  ),
                  const SizedBox(height: 32),
                  Expanded(
                    child: !_loaded
                        ? const Center(child: CircularProgressIndicator())
                        : _cards.isEmpty
                            ? _buildEmptyState(isDarkMode)
                            : _buildCardGrid(isDarkMode),
                  ),
                ],
              ),
            ),
          ),

          Align(
            alignment: Alignment.bottomCenter,
            child: GlassDock(
              currentIndex: widget.currentDockIndex,
              onTap: (index) {
                if (index == 1) {
                  _openCardsList();
                } else {
                  widget.onDockTap(index);
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(bool isDarkMode) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          GlassCard(
            borderRadius: 48,
            child: Container(
              padding: const EdgeInsets.all(40),
              child: Column(
                children: [
                  Container(
                    width: 80, height: 80,
                    decoration: BoxDecoration(
                      color: const Color(0xFF007AFF).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: const Icon(Icons.nfc_rounded, size: 40, color: Color(0xFF007AFF)),
                  ),
                  const SizedBox(height: 20),
                  Text("No Cards Yet", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, letterSpacing: -0.5, color: isDarkMode ? Colors.white : const Color(0xFF1C1C1E))),
                  const SizedBox(height: 8),
                  Text("Tap the NFC icon in the dock\nto add your first patient card.", textAlign: TextAlign.center, style: TextStyle(fontSize: 13, color: isDarkMode ? Colors.white54 : Colors.black45, height: 1.5)),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF007AFF),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
                    ),
                    onPressed: () => _showAddCardSheet(context),
                    icon: const Icon(Icons.add_rounded, color: Colors.white),
                    label: const Text("Add Card", style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600)),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCardGrid(bool isDarkMode) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text("My Cards", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: isDarkMode ? Colors.white70 : Colors.black54)),
            Text("${_cards.length} card${_cards.length > 1 ? 's' : ''}", style: const TextStyle(fontSize: 14, color: Colors.black38)),
          ],
        ),
        const SizedBox(height: 16),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.only(bottom: 100),
            itemCount: _cards.length,
            itemBuilder: (context, i) {
              final card = _cards[i];
              return Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: GestureDetector(
                  onTap: () => _showNfcOverlay(card),
                  child: DigitalPatientCard(
                    patientName: card.name,
                    patientId: card.id,
                    hospitalName: "Cura. Hospital",
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

class NfcActiveOverlay extends StatefulWidget {
  final Widget cardWidget;
  final VoidCallback onClose;

  const NfcActiveOverlay({super.key, required this.cardWidget, required this.onClose});

  @override
  State<NfcActiveOverlay> createState() => _NfcActiveOverlayState();
}

class _NfcActiveOverlayState extends State<NfcActiveOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _anim;
  late Animation<double> _rotation;
  late Animation<double> _scale;
  int _secondsLeft = 15;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _anim = AnimationController(vsync: this, duration: const Duration(milliseconds: 350));
    _rotation = Tween<double>(begin: 0.0, end: -1.5708).animate(CurvedAnimation(parent: _anim, curve: Curves.easeOutBack));
    _scale = Tween<double>(begin: 0.8, end: 1.02).animate(CurvedAnimation(parent: _anim, curve: Curves.easeOutBack));
    _anim.forward();
    _startTimer();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_secondsLeft > 1) {
        setState(() => _secondsLeft--);
      } else {
        _close();
      }
    });
  }

  void _close() {
    _timer?.cancel();
    _anim.reverse().then((_) => widget.onClose());
  }

  @override
  void dispose() {
    _timer?.cancel();
    _anim.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black.withOpacity(0.9),
      body: SafeArea(
        child: Stack(
          children: [
            Align(
              alignment: Alignment.topRight,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: IconButton(
                  icon: const Icon(Icons.close_rounded, color: Colors.white70, size: 32),
                  onPressed: _close,
                ),
              ),
            ),
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.contactless_rounded, color: Color(0xFF007AFF), size: 56),
                  const SizedBox(height: 12),
                  const Text("Hold Near Reader", style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold, letterSpacing: -0.5)),
                  const SizedBox(height: 4),
                  Text("Transmitting patient token via HCE (${_secondsLeft}s remaining)", style: const TextStyle(color: Colors.white54, fontSize: 13)),
                  const SizedBox(height: 70),
                  AnimatedBuilder(
                    animation: _anim,
                    builder: (context, child) {
                      return Transform.scale(
                        scale: _scale.value,
                        child: Transform.rotate(
                          angle: _rotation.value,
                          child: SizedBox(width: MediaQuery.of(context).size.width * 0.85, child: widget.cardWidget),
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 60),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}