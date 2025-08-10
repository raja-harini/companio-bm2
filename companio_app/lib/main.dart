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
    Future.delayed(Duration(seconds:2), () {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => HomePage()));
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

class HomePage extends StatelessWidget {
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
