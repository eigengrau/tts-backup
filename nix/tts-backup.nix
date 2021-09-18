{ python3Packages }:
python3Packages.buildPythonApplication {
  pname = "tts-backup";
  version = "0.1.0.3";
  propagatedBuildInputs = (with python3Packages; [ setuptools tkinter ]);
  src = ../.;
}
