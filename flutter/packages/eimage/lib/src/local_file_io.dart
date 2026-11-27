import 'dart:io';

import 'package:flutter/painting.dart';

ImageProvider<Object> localImage(String path) => FileImage(File(path));
