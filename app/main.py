import os
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()
VALID_STATUSES = {"todo", "in_progress", "done"}

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default="todo")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description,
                "status": self.status, "created_at": self.created_at.isoformat()}


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///tasks.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    @app.get("/")
    def index():
        return jsonify({"service": "Task Management API", "version": "1.0.0", "docs": "/api"})

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/ready")
    def ready():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "ready"})
        except SQLAlchemyError:
            return jsonify({"status": "not_ready"}), 503

    @app.get("/api")
    def api_info():
        return jsonify({"endpoints": ["GET /health", "GET /ready", "GET /api/tasks", "GET /api/tasks/<id>", "POST /api/tasks", "PATCH /api/tasks/<id>", "DELETE /api/tasks/<id>"]})

    @app.get("/api/tasks")
    def list_tasks():
        status = request.args.get("status")
        if status and status not in VALID_STATUSES:
            return jsonify({"error": "Invalid status"}), 400
        query = db.select(Task).order_by(Task.id.desc())
        if status:
            query = query.where(Task.status == status)
        return jsonify({"tasks": [task.to_dict() for task in db.session.scalars(query).all()]})

    @app.get("/api/tasks/<int:task_id>")
    def get_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        return jsonify(task.to_dict())

    @app.post("/api/tasks")
    def create_task():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected a JSON object"}), 400
        title = data.get("title")
        description = data.get("description", "")
        status = data.get("status", "todo")
        if not isinstance(title, str) or not title.strip() or len(title.strip()) > 160:
            return jsonify({"error": "title must be 1-160 characters"}), 400
        if not isinstance(description, str) or len(description) > 5000:
            return jsonify({"error": "description must be a string up to 5000 characters"}), 400
        if status not in VALID_STATUSES:
            return jsonify({"error": "status must be todo, in_progress, or done"}), 400
        task = Task(title=title.strip(), description=description, status=status)
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201

    @app.patch("/api/tasks/<int:task_id>")
    def update_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Expected a JSON object"}), 400
        if not data or any(k not in {"title", "description", "status"} for k in data):
            return jsonify({"error": "Provide only title, description, or status"}), 400
        if "title" in data:
            title = data["title"]
            if not isinstance(title, str) or not title.strip() or len(title.strip()) > 160:
                return jsonify({"error": "title must be 1-160 characters"}), 400
            task.title = title.strip()
        if "description" in data:
            if not isinstance(data["description"], str) or len(data["description"]) > 5000:
                return jsonify({"error": "description must be a string up to 5000 characters"}), 400
            task.description = data["description"]
        if "status" in data:
            if data["status"] not in VALID_STATUSES:
                return jsonify({"error": "Invalid status"}), 400
            task.status = data["status"]
        db.session.commit()
        return jsonify(task.to_dict())

    @app.delete("/api/tasks/<int:task_id>")
    def delete_task(task_id):
        task = db.session.get(Task, task_id)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        db.session.delete(task)
        db.session.commit()
        return "", 204

    with app.app_context():
        db.create_all()  # For student bootstrap; replace with Alembic migrations in production.
    return app

app = create_app()
