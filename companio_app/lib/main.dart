import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(CompanioApp());

class CompanioApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Companio',
      theme: ThemeData(primarySwatch: Colors.teal),
      home: SplashScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class SplashScreen extends StatefulWidget {
  @override
  _SplashScreenState createState() => _SplashScreenState();
}
class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(Duration(seconds: 2), () {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => InitialPage()));
    });
  }
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.watch, size: 96, color: Colors.teal),
          SizedBox(height:16),
          Text('Companio', style: TextStyle(fontSize:28, fontWeight: FontWeight.bold)),
        ]),
      ),
    );
  }
}

// NEW Initial page with 2 buttons
class InitialPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Companio")),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ElevatedButton(
              child: Text("Companio"),
              onPressed: () {
                Navigator.push(context, MaterialPageRoute(builder: (_) => CompanioControlPage()));
              },
            ),
            SizedBox(height: 20),
            ElevatedButton(
              child: Text("Health Monitor"),
              onPressed: () {
                Navigator.push(context, MaterialPageRoute(builder: (_) => HealthMonitorPage()));
              },
            ),
          ],
        ),
      ),
    );
  }
}

// Your existing CompanioControlPage (renamed HomePage -> CompanioControlPage)
class CompanioControlPage extends StatelessWidget {
  // IMPORTANT: use "localhost" because adb reverse forwards device localhost to host.
  final String server = "http://localhost:5000";
  // Put your dev CONTROL_API_KEY here (must match server .env).
  static const String CONTROL_API_KEY = "1zVx8P4QfE9mU6sT2bW7yH0jR3dL8cKq";

  final Map<String,String> headers = {
    "Content-Type": "application/json",
    "X-API-KEY": CONTROL_API_KEY
  };

  Future<void> _startLang(BuildContext ctx, String lang) async {
    final url = Uri.parse("$server/start/${lang.toLowerCase()}");
    try {
      final resp = await http.post(url, headers: headers).timeout(Duration(seconds:8));
      ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text("Start ${lang}: ${resp.statusCode}")));
    } catch (e) {
      ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  Future<void> _stopLang(BuildContext ctx, String lang) async {
    final url = Uri.parse("$server/stop/${lang.toLowerCase()}");
    try {
      final resp = await http.post(url, headers: headers).timeout(Duration(seconds:8));
      ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text("Stop ${lang}: ${resp.statusCode}")));
    } catch (e) {
      ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Companio Control")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(children: [
          Text("Choose language", style: TextStyle(fontSize:18)),
          SizedBox(height:24),
          Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            ElevatedButton(onPressed: () => _startLang(context,"English"), child: Text("English")),
            ElevatedButton(onPressed: () => _startLang(context,"Tamil"), child: Text("Tamil")),
            ElevatedButton(onPressed: () => _startLang(context,"Hindi"), child: Text("Hindi")),
          ]),
          SizedBox(height:12),
          Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            OutlinedButton(onPressed: () => _stopLang(context,"English"), child: Text("Stop En")),
            OutlinedButton(onPressed: () => _stopLang(context,"Tamil"), child: Text("Stop Ta")),
            OutlinedButton(onPressed: () => _stopLang(context,"Hindi"), child: Text("Stop Hi")),
          ]),
          SizedBox(height:24),
          ElevatedButton(
              onPressed: () async {
                // status check
                final url = Uri.parse("$server/status");
                try {
                  final resp = await http.get(url, headers: headers);
                  final map = jsonDecode(resp.body);
                  final text = map.entries.map((e) => "${e.key}:${e.value}").join(", ");
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Status error: $e")));
                }
              },
              child: Text("Check Status")
          )
        ]),
      ),
    );
  }
}

// NEW HealthMonitorPage with language buttons calling /health_monitor/start
class HealthMonitorPage extends StatelessWidget {
  final String server = "http://localhost:5000";
  static const String CONTROL_API_KEY = "1zVx8P4QfE9mU6sT2bW7yH0jR3dL8cKq";

  final Map<String,String> headers = {
    "Content-Type": "application/json",
    "X-API-KEY": CONTROL_API_KEY
  };

  Future<void> _startHealthMonitor(BuildContext ctx, String language) async {
    final url = Uri.parse("$server/health_monitor/start");
    try {
      final resp = await http.post(
        url,
        headers: headers,
        body: jsonEncode({"language": language}),
      ).timeout(Duration(seconds: 8));
      if (resp.statusCode == 200) {
        ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text("Health Monitor started for $language")));
      } else {
        ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text("Failed to start: ${resp.body}")));
      }
    } catch (e) {
      ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  Future<void> _stopHealthMonitor(BuildContext ctx) async {
    final url = Uri.parse("$server/health_monitor/stop");
    try {
      final resp = await http.post(url, headers: headers).timeout(Duration(seconds: 8));
      if (resp.statusCode == 200) {
        ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text("Health Monitor stopped")));
      }
    } catch (e) {
      ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text("Error stopping: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Health Monitor")),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            Text("Select Language", style: TextStyle(fontSize: 18)),
            SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                ElevatedButton(
                    onPressed: () => _startHealthMonitor(context, "English"),
                    child: Text("English")),
                ElevatedButton(
                    onPressed: () => _startHealthMonitor(context, "Tamil"),
                    child: Text("Tamil")),
                ElevatedButton(
                    onPressed: () => _startHealthMonitor(context, "Hindi"),
                    child: Text("Hindi")),
              ],
            ),
            SizedBox(height: 24),
            ElevatedButton(
                onPressed: () => _stopHealthMonitor(context),
                child: Text("Stop Health Monitor"))
          ],
        ),
      ),
    );
  }
}
