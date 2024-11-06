import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from rules import d_rule

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Выбор файла и параметров")

        self.file_path = None
        self.column_headers = []

        self.create_widgets()

    def create_widgets(self):
        self.file_label = tk.Label(self.root, text="Выберите файл")
        self.file_label.pack(pady=10)

        self.file_button = tk.Button(self.root, text="Выбрать файл", command=self.select_file)
        self.file_button.pack()

        self.column_label = tk.Label(self.root, text="Выберите от 1 до 3 столбцов:")
        self.column_label.pack(pady=10)

        self.columns_frame = tk.Frame(self.root)
        self.columns_frame.pack(anchor="w", padx=20)

        self.column_vars = []
        self.column_checkboxes = []

        self.single_column_label = tk.Label(self.root, text="Выберите один столбец:")
        self.single_column_label.pack(pady=10)

        self.single_column_var = tk.StringVar(self.root)
        self.single_column_dropdown = tk.OptionMenu(self.root, self.single_column_var, [])
        self.single_column_dropdown.pack()

        self.choice_var = tk.StringVar()
        self.choice_var.set("expert")

        self.expert_radio = tk.Radiobutton(self.root, text="Экспертная оценка", variable=self.choice_var,
                                           value="expert")
        self.expert_radio.pack(anchor="w")

        self.uniform_radio = tk.Radiobutton(self.root, text="Равномерное распределение", variable=self.choice_var,
                                            value="uniform")
        self.uniform_radio.pack(anchor="w")

        self.open_button = tk.Button(self.root, text="Открыть", command=self.open_selected)
        self.open_button.pack(pady=20)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not self.file_path:
            return

        try:
            df = pd.read_csv(self.file_path)
            self.column_headers = list(df.columns)

            self.update_column_selection()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def update_column_selection(self):
        for checkbox in self.column_checkboxes:
            checkbox.destroy()
        self.column_checkboxes.clear()
        self.column_vars.clear()

        for col in self.column_headers:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(self.columns_frame, text=col, variable=var)
            checkbox.pack(anchor="w")
            self.column_checkboxes.append(checkbox)
            self.column_vars.append(var)

        menu = self.single_column_dropdown["menu"]
        menu.delete(0, "end")
        for col in self.column_headers:
            menu.add_command(label=col, command=lambda value=col: self.single_column_var.set(value))

    def open_selected(self):
        selected_columns = [col for var, col in zip(self.column_vars, self.column_headers) if var.get()]
        single_column = self.single_column_var.get()

        if not selected_columns or not single_column:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите столбцы")
            return

        if len(selected_columns) > 3:
            messagebox.showwarning("Предупреждение", "Можно выбрать не более 3 столбцов")
            return

        if self.choice_var.get() == "expert":
            self.open_expert_window(selected_columns, single_column)
        else:
            self.open_uniform_window(selected_columns, single_column)

    def open_expert_window(self, columns, single_column):
        expert_window = tk.Toplevel(self.root)
        expert_window.title("Экспертная оценка")

        tk.Label(expert_window, text="Выберите функцию принадлежности:").pack(anchor="w")
        self.expert_membership_func = tk.StringVar(expert_window)
        membership_options = ["Треугольная", "Трапециевидная", "Квадратная", "Гаусса"]
        membership_dropdown = tk.OptionMenu(expert_window, self.expert_membership_func, *membership_options,
                                            command=self.show_interval_selection)
        membership_dropdown.pack(anchor="w")

        self.expert_params_frame = tk.Frame(expert_window)
        self.expert_params_frame.pack(anchor="w", pady=10)

        self.expert_next_button = tk.Button(expert_window, text="Далее", command=self.on_expert_next)
        self.expert_next_button.pack(pady=10)

    def show_interval_selection(self, *args):
        for widget in self.expert_params_frame.winfo_children():
            widget.destroy()

        tk.Label(self.expert_params_frame, text="Количество интервалов (от 2 до 6):").pack(anchor="w")
        self.num_intervals_var = tk.IntVar(value=2)
        intervals_dropdown = tk.OptionMenu(self.expert_params_frame, self.num_intervals_var, *range(2, 7),
                                           command=self.update_expert_fields)
        intervals_dropdown.pack(anchor="w")

    def update_expert_fields(self, *args):
        for widget in self.expert_params_frame.winfo_children():
            widget.destroy()

        func = self.expert_membership_func.get()
        num_intervals = self.num_intervals_var.get()

        columns = [col for var, col in zip(self.column_vars, self.column_headers) if var.get()]
        columns.append(self.single_column_var.get())

        if func == "Треугольная":
            params = ["a", "b", "c"]
        elif func == "Трапециевидная":
            params = ["a", "b", "c", "d"]
        elif func == "Квадратная":
            params = ["a", "b", "c"]
        elif func == "Гаусса":
            params = ["Мат ожидание", "Среднеквадр отклонение"]

        for index, col in enumerate(columns):
            col_frame = tk.LabelFrame(self.expert_params_frame, text=f"Параметры для столбца {col}")
            col_frame.grid(row=index // 2, column=index % 2, padx=10, pady=5,
                           sticky="nsew")

            for i in range(num_intervals):
                interval_frame = tk.Frame(col_frame)
                interval_frame.pack(anchor="w", pady=5)
                tk.Label(interval_frame, text=f"Интервал {i + 1}").pack(anchor="w")

                for j, param in enumerate(params):
                    param_frame = tk.Frame(interval_frame)
                    param_frame.pack(side="left", padx=5)
                    tk.Label(param_frame, text=f"{param} значения: ").pack(side="left")
                    entry = tk.Entry(param_frame, width=10)
                    entry.pack(side="left")

                term_label = tk.Label(interval_frame, text=f"Терм {i + 1}:")
                term_label.pack(anchor="w")
                term_entry = tk.Entry(interval_frame)
                term_entry.pack(anchor="w", padx=5, pady=2)

        for i in range((len(columns) + 1) // 2):
            self.expert_params_frame.grid_rowconfigure(i, weight=1)
        self.expert_params_frame.grid_columnconfigure(0, weight=1)
        self.expert_params_frame.grid_columnconfigure(1, weight=1)

    def on_expert_next(self):
        selected_func = self.expert_membership_func.get()
        num_intervals = self.num_intervals_var.get()
        func_params = {}

        for col_frame in self.expert_params_frame.winfo_children():
            col_name = col_frame.cget("text").replace("Параметры для столбца ", "")
            intervals_data = []

            for interval_frame in col_frame.winfo_children():
                interval_data = {}
                for widget in interval_frame.winfo_children():
                    if isinstance(widget, tk.Entry):
                        parent = widget.winfo_parent()
                        if isinstance(parent, tk.Frame):
                            param_name_widget = parent.winfo_children()[0]
                            if isinstance(param_name_widget, tk.Label):
                                param_name = param_name_widget.cget("text").replace(" значения:", "")
                                interval_data[param_name] = widget.get()  # Сохраняем значение из Entry
                    elif isinstance(widget, tk.Label) and "Терм" in widget.cget("text"):
                        term_name = widget.cget("text").replace("Терм ", "")

                        entry_found = False
                        for child in interval_frame.winfo_children():
                            if isinstance(child, tk.Entry) and entry_found:
                                interval_data[term_name] = child.get()
                                break
                            if child == widget:
                                entry_found = True

                if interval_data:
                    intervals_data.append(interval_data)

            func_params[col_name] = intervals_data

    def open_uniform_window(self, columns, single_column):
        self.uniform_window = tk.Toplevel(self.root)
        self.uniform_window.title("Равномерное распределение")

        tk.Label(self.uniform_window, text="Выберите функцию принадлежности:").pack(anchor="w")

        self.membership_func = tk.StringVar(self.uniform_window)
        membership_options = ["Гаусса", "Квадратная", "Треугольная", "Трапециевидная"]
        membership_dropdown = tk.OptionMenu(self.uniform_window, self.membership_func, *membership_options)
        membership_dropdown.pack(anchor="w")

        tk.Label(self.uniform_window, text="Количество интервалов (от 2 до 6):").pack(anchor="w")
        self.num_intervals_var = tk.IntVar(value=2)
        intervals_dropdown = tk.OptionMenu(self.uniform_window, self.num_intervals_var, *range(2, 7),
                                           command=self.update_terms_fields)
        intervals_dropdown.pack(anchor="w")

        self.terms_frame = tk.Frame(self.uniform_window)
        self.terms_frame.pack(anchor="w", pady=10)

        self.update_terms_fields()

        self.next_button = tk.Button(self.uniform_window, text="Далее", command=self.on_next)
        self.next_button.pack(pady=10)

    def update_terms_fields(self, *args):
        for widget in self.terms_frame.winfo_children():
            widget.destroy()

        num_intervals = self.num_intervals_var.get()

        all_columns = [var for var, selected in zip(self.column_headers, self.column_vars) if selected.get()]
        all_columns.append(self.single_column_var.get())

        for col in all_columns:
            col_frame = tk.LabelFrame(self.terms_frame, text=f"Термы для столбца {col}")
            col_frame.pack(anchor="w", fill="x", padx=10, pady=5)

            for i in range(num_intervals):
                term_label = tk.Label(col_frame, text=f"Терм {i + 1}:")
                term_label.grid(row=i, column=0, padx=5, pady=2)
                term_entry = tk.Entry(col_frame)
                term_entry.grid(row=i, column=1, padx=5, pady=2)

    def on_next(self):
        selected_func = self.membership_func.get()
        num_intervals = self.num_intervals_var.get()
        intervals_data = {}

        for frame in self.terms_frame.winfo_children():
            col_name = frame.cget("text").replace("Термы для столбца ", "")
            terms = [entry.get() for entry in frame.winfo_children() if isinstance(entry, tk.Entry)]
            intervals_data[col_name] = terms

        try:
            df = pd.read_csv(self.file_path)

            selected_columns = [col for var, col in zip(self.column_vars, self.column_headers) if var.get()]

            additional_column = self.single_column_var.get()

            if selected_columns:
                if additional_column and additional_column in df.columns:
                    selected_columns.append(additional_column)

                selected_columns_data = df[selected_columns]
            else:
                selected_columns_data = None

        except Exception as e:
            selected_columns_data = None

        print(intervals_data)
        d_rule(selected_func, num_intervals, selected_columns_data, intervals_data)


        messagebox.showinfo("Результат", "Параметры успешно обработаны")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
