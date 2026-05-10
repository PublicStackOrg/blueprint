import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(const ProviderScope(child: App()));
}

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '{{ cookiecutter.app_name }}',
      home: Scaffold(
        appBar: AppBar(title: const Text('{{ cookiecutter.app_name }}')),
        body: const Center(child: Text('Hello, {{ cookiecutter.app_name }}!')),
      ),
    );
  }
}
