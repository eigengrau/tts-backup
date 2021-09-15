{ pkgs }:
pkgs.python38Packages.buildPythonApplication {
  pname = "tts-backup";
  version = "0.1.0.3";
  propagatedBuildInputs = (with pkgs.python38Packages; [ setuptools tkinter ]);
  src = ../.;
}
