// SPDX-License-Identifier: AGPL-3.0-or-later
// Part of {{ cookiecutter.public_service_name }} (PublicStack).
//
// Thin Dio wrapper. Holds the base URL and an auth-token slot. Real
// auth wiring lands in Phase 4 with the Grid identity adapter.

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ApiClient {
  ApiClient({required this.baseUrl}) : _dio = Dio(BaseOptions(baseUrl: baseUrl));

  final String baseUrl;
  final Dio _dio;

  String? _authToken;

  void setAuthToken(String? token) {
    _authToken = token;
    if (token == null) {
      _dio.options.headers.remove('Authorization');
    } else {
      _dio.options.headers['Authorization'] = 'Bearer $token';
    }
  }

  Future<Response<T>> get<T>(String path, {Map<String, dynamic>? query}) {
    return _dio.get<T>(path, queryParameters: query);
  }

  Future<Response<T>> post<T>(String path, {Object? data}) {
    return _dio.post<T>(path, data: data);
  }

  Future<Response<T>> delete<T>(String path) {
    return _dio.delete<T>(path);
  }
}

final apiClientProvider = Provider<ApiClient>((ref) {
  // Override at app boot with the right base URL (env-driven).
  throw UnimplementedError(
    'apiClientProvider must be overridden at app boot via ProviderScope(overrides: [...]).',
  );
});
