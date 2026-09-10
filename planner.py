import customtkinter as ctk

# Sample Global/State Task List
tasks_db = [
    {"id": 1, "title": "Review AI Model Prompting", "time": "09:00 AM", "completed": True},
    {"id": 2, "title": "Debug Dashboard Layout", "time": "11:30 AM", "completed": False},
    {"id": 3, "title": "Integrate Voice Recognition", "time": "04:00 PM", "completed": False},
]

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback):
        super().__init__(parent)
        self.navigate_callback = navigate_callback

        # Header
        ctk.CTkLabel(self, text="Dashboard", font=("Arial", 22, "bold")).pack(anchor="w", padx=20, pady=(20, 10))

        # --- PLAN YOUR DAY WIDGET (Card) ---
        widget_card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e2e")
        widget_card.pack(fill="x", padx=20, pady=10)

        # Widget Title & Navigation Button
        top_frame = ctk.CTkFrame(widget_card, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=(12, 5))
        
        ctk.CTkLabel(top_frame, text="📅 Plan Your Day", font=("Arial", 16, "bold"), text_color="#ffffff").pack(side="left")
        
        nav_btn = ctk.CTkButton(
            top_frame, 
            text="Open Planner →", 
            width=110, 
            height=28,
            command=lambda: self.navigate_callback("planner")
        )
        nav_btn.pack(side="right")

        # Completion Status Progress
        completed_count = sum(1 for t in tasks_db if t["completed"])
        total_count = len(tasks_db)
        status_text = f"Completed: {completed_count}/{total_count}" if total_count > 0 else "No tasks planned yet"
        
        ctk.CTkLabel(widget_card, text=status_text, font=("Arial", 12), text_color="#a6adc8").pack(anchor="w", padx=15, pady=(0, 10))

        # Quick Task Preview (Top 3 Pending / Tasks)
        preview_frame = ctk.CTkFrame(widget_card, fg_color="transparent")
        preview_frame.pack(fill="x", padx=15, pady=(0, 12))

        for task in tasks_db[:3]:
            row = ctk.CTkFrame(preview_frame, fg_color="#2b2b3b", height=32, corner_radius=6)
            row.pack(fill="x", pady=3)
            
            status_icon = "✔" if task["completed"] else "⏳"
            task_label = f"{status_icon} [{task['time']}] {task['title']}"
            
            lbl = ctk.CTkLabel(row, text=task_label, font=("Arial", 13), text_color="#cdd6f4")
            lbl.pack(side="left", padx=10)


class PlanYourDayView(ctk.CTkFrame):
    def __init__(self, parent, navigate_callback):
        super().__init__(parent)
        self.navigate_callback = navigate_callback

        # Header with Back Button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        back_btn = ctk.CTkButton(header_frame, text="← Back to Dashboard", width=120, command=lambda: self.navigate_callback("dashboard"))
        back_btn.pack(side="left")

        ctk.CTkLabel(header_frame, text="Plan Your Day", font=("Arial", 22, "bold")).pack(side="left", padx=20)

        # Input Form (Add New Task)
        input_card = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=10)
        input_card.pack(fill="x", padx=20, pady=10)

        self.title_entry = ctk.CTkEntry(input_card, placeholder_text="Task description (e.g., Study Vectors)", width=280)
        self.title_entry.pack(side="left", padx=(15, 10), pady=15, expand=True, fill="x")

        self.time_entry = ctk.CTkEntry(input_card, placeholder_text="Time (e.g., 10:30 AM)", width=140)
        self.time_entry.pack(side="left", padx=10, pady=15)

        add_btn = ctk.CTkButton(input_card, text="+ Add Task", fg_color="#a6e3a1", text_color="#11111b", hover_color="#94e2d5", command=self.add_task)
        add_btn.pack(side="left", padx=(10, 15), pady=15)

        # Scrollable Task List
        self.list_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.render_tasks()

    def render_tasks(self):
        # Clear existing widgets
        for widget in self.list_container.winfo_children():
            widget.destroy()

        for task in tasks_db:
            card = ctk.CTkFrame(self.list_container, fg_color="#1e1e2e", corner_radius=8)
            card.pack(fill="x", pady=5)

            # Completion Checkbox
            var = ctk.BooleanVar(value=task["completed"])
            
            def make_toggle(t=task):
                return lambda: self.toggle_task(t)

            chk = ctk.CTkCheckBox(
                card, 
                text=f"[{task['time']}]  {task['title']}", 
                variable=var, 
                command=make_toggle(),
                font=("Arial", 14),
                checkbox_width=20,
                checkbox_height=20
            )
            chk.pack(side="left", padx=15, pady=12)

            # Status Badge
            status_color = "#a6e3a1" if task["completed"] else "#f9e2af"
            status_str = "Completed" if task["completed"] else "Pending"
            
            badge = ctk.CTkLabel(card, text=status_str, text_color=status_color, font=("Arial", 11, "bold"))
            badge.pack(side="right", padx=15)

    def add_task(self):
        title = self.title_entry.get().strip()
        time_str = self.time_entry.get().strip()

        if title and time_str:
            new_id = len(tasks_db) + 1
            tasks_db.append({"id": new_id, "title": title, "time": time_str, "completed": False})
            self.title_entry.delete(0, 'end')
            self.time_entry.delete(0, 'end')
            self.render_tasks()

    def toggle_task(self, task):
        task["completed"] = not task["completed"]
        self.render_tasks()


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Project Dashboard & Planner")
        self.geometry("700x500")
        ctk.set_appearance_mode("dark")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.views = {}
        self.show_view("dashboard")

    def show_view(self, view_name):
        # Clear frame
        for widget in self.container.winfo_children():
            widget.destroy()

        if view_name == "dashboard":
            view = DashboardView(self.container, self.show_view)
        elif view_name == "planner":
            view = PlanYourDayView(self.container, self.show_view)

        view.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()