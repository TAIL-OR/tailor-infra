import subprocess

libraries = [
    "mlforecast",
    "pandas",
    "numpy",
    "xgboost",
    "lightgbm",
    "optuna",
    "matplotlib",
    "holidays",
    "scikit-learn"
]

with open("requirements.txt", "a") as f:
    for lib in libraries:
        # Obtendo a versão instalada da biblioteca
        version = subprocess.check_output(["pip", "show", lib]).decode("utf-8")
        version = [line for line in version.split("\n") if line.startswith("Version:")][0]
        version = version.split(": ")[1].strip()
        
        # Escrevendo no arquivo requirements.txt
        f.write(f"{lib}=={version}\n")