import 'package:intl/intl.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:todo_flutter/model/task_model.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper.internal();

  factory DatabaseHelper() => _instance;

  Database? _db;

  DatabaseHelper.internal();

  Future<Database> get db async {
    if (_db != null) {
      return _db!;
    }
    _db = await initDb();
    return _db!;
  }

  Future<Database> initDb() async {
    String databasesPath = await getDatabasesPath();
    String path = join(databasesPath, 'Todo.db');

    var db = await openDatabase(
      path,
      version: 3,
      onCreate: (Database db, int version) async {
        await db.execute('''
          CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            success BOOLEAN NOT NULL DEFAULT false
          );
          CREATE TABLE shared_with (
            id INTEGER PRIMARY KEY,
            task_id INTEGER NOT NULL,
            friend_name TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
          );
          
        ''');
      },
    );

    return db;
  }

  Future<int> insertTask(Task task) async {
    var client = await db;
    return await client.insert(
      'tasks',
      task.toMap(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<int> insertSharedWith(int taskId, String friendName) async {
    var client = await db;
    return await client.insert(
      'shared_with',
      {
        'task_id': taskId,
        'friend_name': friendName,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Task>> getAllTasks() async {
    var client = await db;
    var tasks = await client.query('tasks');
    return tasks.map((taskMap) => Task.fromMap(taskMap)).toList();
  }

  Future<int> updateTask(Task task) async {
    var client = await db;
    return await client.update(
      'tasks',
      task.toMap(),
      where: 'id = ?',
      whereArgs: [task.id],
    );
  }

  Future<int> deleteTask(int taskId) async {
    var client = await db;
    return await client.delete(
      'tasks',
      where: 'id = ?',
      whereArgs: [taskId],
    );
  }

  // Dodanie true do pola insucces w tasku
  Future<int> markTaskAsInSuccess(int taskId) async {
    var client = await db;
    return await client.update(
      'tasks',
      {'success': true},
      where: 'id = ?',
      whereArgs: [taskId],
    );
  }
  // Zliczanie ukończonych tasków
  Future<int> countAllTasksComplete() async {
    var client = await db;
    var result = await client.rawQuery('SELECT COUNT(*) FROM tasks WHERE success = ?', [true]);
    int count = Sqflite.firstIntValue(result) ?? 0;
    return count;
  }

// Zliczanie tasków nieukończonych licząc od wczorajszego dnia
  Future<int> countIncompleteTasksFromYesterday() async {
    var client = await db;
    DateTime now = DateTime.now();
    DateTime yesterday = now.subtract(Duration(days: 1));
    var result = await client.rawQuery(
      'SELECT COUNT(*) FROM tasks WHERE success = ? AND date <= ?',
      [0, DateFormat('yyyy-MM-dd').format(yesterday)],
    );
    int count = Sqflite.firstIntValue(result) ?? 0;
    return count;
  }

  // Zliczanie wszystki tasków które nie są ukończone ale nie są po terminie
  Future<int> countAllTasks() async {
    var client = await db;
    DateTime now = DateTime.now();
    var result = await client.rawQuery(
      'SELECT COUNT(*) FROM tasks WHERE date >= ? AND success = ?',
      [DateFormat('yyyy-MM-dd').format(now), 0],
    );
    int count = Sqflite.firstIntValue(result) ?? 0;
    return count;
  }

}