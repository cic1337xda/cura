import 'package:flutter/material.dart';
import 'glass_card.dart';

class DigitalPatientCard extends StatelessWidget {
  final String patientName;
  final String patientId;
  final String hospitalName;

  const DigitalPatientCard({
    Key? key,
    required this.patientName,
    required this.patientId,
    required this.hospitalName,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : Colors.black87;
    final subColor = isDark ? Colors.white54 : Colors.black54;

    return GlassCard(
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  hospitalName.toUpperCase(),
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, letterSpacing: 2.0, color: textColor),
                ),
                Icon(Icons.contactless_rounded, size: 28, color: isDark ? Colors.tealAccent : Colors.teal),
              ],
            ),
            const SizedBox(height: 40),
            Text("PATIENT NAME", style: TextStyle(fontSize: 12, color: subColor, letterSpacing: 1.0)),
            Text(patientName, style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: textColor)),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text("PATIENT ID", style: TextStyle(fontSize: 10, color: subColor, letterSpacing: 1.0)),
                    Text(patientId, style: TextStyle(fontSize: 16, fontFamily: 'Courier', fontWeight: FontWeight.bold, color: textColor)),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.teal.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.check_circle, size: 14, color: Colors.teal),
                      SizedBox(width: 4),
                      Text("NFC READY", style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.teal)),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
