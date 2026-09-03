import 'dart:ui';
import 'package:flutter/material.dart';

class GlassDock extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const GlassDock({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 20),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(32),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 25, sigmaY: 25),
          child: Container(
            height: 76,
            decoration: BoxDecoration(
              color: isDarkMode
                  ? Colors.black.withOpacity(0.4)
                  : Colors.white.withOpacity(0.35),
              borderRadius: BorderRadius.circular(32),
              border: Border.all(
                color: Colors.white.withOpacity(0.2),
                width: 1.2,
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: _buildDockItems(context),
            ),
          ),
        ),
      ),
    );
  }

  List<Widget> _buildDockItems(BuildContext context) {
    final icons = [Icons.home_rounded, Icons.nfc_rounded];

    return List.generate(icons.length, (index) {
      final isSelected = currentIndex == index;
      return GestureDetector(
        onTap: () => onTap(index),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOutBack,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: isSelected
                ? Theme.of(context).primaryColor.withOpacity(0.15)
                : Colors.transparent,
            shape: BoxShape.circle,
          ),
          child: Icon(
            icons[index],
            size: 28,
            color: isSelected
                ? Theme.of(context).primaryColor
                : Theme.of(context).iconTheme.color?.withOpacity(0.5),
          ),
        ),
      );
    });
  }
}