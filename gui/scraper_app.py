import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import re
import csv
from fetchers.scraper import GithubScraper
from fetchers.api_fetcher import GithubApiFetcher

class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Buscador")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        self.repo_queue = []
        self.results_queue = queue.Queue()
        self.tree_item_ids = {}

        self.create_widgets()
        self.process_results_queue()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="Adcionar Repositório URL", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        self.url_entry = ttk.Entry(input_frame, width=60)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.url_entry.bind("<Return>", self.add_repo_from_entry)

        self.add_button = ttk.Button(input_frame, text="Adcionar a Fila", command=self.add_repo_from_entry)
        self.add_button.pack(side=tk.LEFT)

        queue_control_frame = ttk.Frame(main_frame)
        queue_control_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        queue_frame = ttk.LabelFrame(queue_control_frame, text="Processando File", padding="10")
        queue_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.repo_listbox = tk.Listbox(queue_frame, height=10, selectmode=tk.SINGLE)
        self.repo_listbox.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(queue_control_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))

        self.start_api_button = ttk.Button(
            control_frame,
            text="Buscar por API",
            command=lambda: self.start_processing(use_api=True)
        )
        self.start_api_button.pack(fill=tk.X, pady=2)

        self.start_scrape_button = ttk.Button(
            control_frame,
            text="Buscar por Scraping",
            command=lambda: self.start_processing(use_api=False)
        )
        self.start_scrape_button.pack(fill=tk.X, pady=2)

        self.save_csv_button = ttk.Button(control_frame, text="Salvar em CSV", command=self.save_to_csv)
        self.save_csv_button.pack(fill=tk.X, pady=(10, 2))

        self.clear_queue_button = ttk.Button(control_frame, text="Limpar Fila", command=self.clear_queue)
        self.clear_queue_button.pack(fill=tk.X, pady=2)

        self.clear_results_button = ttk.Button(control_frame, text="Limpar Resultados", command=self.clear_results)
        self.clear_results_button.pack(fill=tk.X, pady=2)

        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.columns = ("repositório", "linguagem", "estrela", "forks")
        self.results_tree = ttk.Treeview(results_frame, columns=self.columns, show="headings")

        for col in self.columns:
            self.results_tree.heading(col, text=col.capitalize())
            self.results_tree.column(col, width=150, anchor=tk.W)

        self.results_tree.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Pronto para adcionar URLs a fila")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def add_repo_from_entry(self, event=None):
        url = self.url_entry.get().strip()
        if not url:
            return

        match = re.search(r"github\.com/([\w.-]+/[\w.-]+)", url)
        if match:
            repo_path = match.group(1)
            if repo_path not in self.repo_queue:
                self.repo_queue.append(repo_path)
                self.repo_listbox.insert(tk.END, repo_path)
                self.url_entry.delete(0, tk.END)
                self.status_var.set(f"Adcionado '{repo_path}' na fila.")
            else:
                messagebox.showwarning("Duplicado", f"'{repo_path}' já está na fila.")
        else:
            messagebox.showerror("URL inválida", "Digite uma URL do GitHub válido")

    def clear_queue(self):
        self.repo_queue.clear()
        self.repo_listbox.delete(0, tk.END)
        self.status_var.set("Fila Limpa")

    def clear_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.tree_item_ids.clear()
        self.status_var.set("Resultados Limpos")

    def save_to_csv(self):
        if not self.results_tree.get_children():
            messagebox.showinfo("Sem dados", "Não há dados para serem salvos")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV ", "*.csv"), ("Todos os arquivos", "*.*")],
            title="Salvar resultados como"
        )

        if not filepath:
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.columns)
                for item_id in self.results_tree.get_children():
                    row_values = self.results_tree.item(item_id, "values")
                    writer.writerow(row_values)

            self.status_var.set(f"Os resultados foram salvos em {filepath}")
            messagebox.showinfo("Tudo Certo!", "Os resultados foram salvos em CSV")
        except IOError as e:
            self.status_var.set("Erro ao salvar arquivo")
            messagebox.showerror("Erro ao Salvar Arquivo", f"Ocorreu um erro ao salvar o arquivo:\n{e}")

    def start_processing(self, use_api):
        if not self.repo_queue:
            messagebox.showinfo("Fila Vazia", "A fila de processos está vazia")
            return

        self.toggle_buttons(enabled=False)
        threads = []
        repos_to_process = list(self.repo_queue)
        method_str = "API" if use_api else "Scraping"
        self.status_var.set(f"Realizando {method_str} para {len(repos_to_process)} repositorios...")

        for repo_path in repos_to_process:
            loading_values = (repo_path, "carregando...", "carregando...", "carregando...")
            item_id = self.results_tree.insert("", tk.END, values=loading_values)
            self.tree_item_ids[repo_path] = item_id

            try:
                owner, repo = repo_path.split('/')
                target_worker = self._api_worker if use_api else self._scrape_worker
                fetcher_instance = GithubApiFetcher(owner, repo) if use_api else GithubScraper(owner, repo)

                thread = threading.Thread(target=target_worker, args=(fetcher_instance,), daemon=True)
                threads.append(thread)
                thread.start()
            except ValueError:
                error_data = {
                    "repository": repo_path,
                    "language": "Invalid Path",
                    "stars": "N/A",
                    "forks": "N/A"
                }
                self.results_queue.put(error_data)

        self.clear_queue()

        monitor = threading.Thread(target=self._monitor_threads, args=(threads,), daemon=True)
        monitor.start()

    def _scrape_worker(self, scraper_instance):
        data = scraper_instance.scrape()
        if data:
            self.results_queue.put(data)

    def _api_worker(self, fetcher_instance):
        data = fetcher_instance.fetch()
        if data:
            self.results_queue.put(data)

    def _monitor_threads(self, threads):
        for thread in threads:
            thread.join()
        self.root.after(0, self.on_all_tasks_complete)

    def on_all_tasks_complete(self):
        self.status_var.set("Todas tarefas finalizadas")
        self.toggle_buttons(enabled=True)

    def toggle_buttons(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.start_api_button.config(state=state)
        self.start_scrape_button.config(state=state)
        self.clear_queue_button.config(state=state)

        if enabled and self.results_tree.get_children():
            self.save_csv_button.config(state=tk.NORMAL)
        else:
            self.save_csv_button.config(state=state)

    def process_results_queue(self):
        try:
            while True:
                result = self.results_queue.get_nowait()
                self.update_result_in_tree(result)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_results_queue)

    def update_result_in_tree(self, result):
        if not result:
            return

        repo_path = result.get("repository")
        item_id = self.tree_item_ids.get(repo_path)

        if item_id:
            final_values = (
                repo_path,
                result.get("language", "N/A"),
                result.get("stars", "N/A"),
                result.get("forks", "N/A"),
            )
            self.results_tree.item(item_id, values=final_values)
