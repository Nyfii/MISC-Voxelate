{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = [
    pkgs.python313
    pkgs.python313Packages.pip
    pkgs.python313Packages.virtualenv
    pkgs.python313Packages.imageio
  ];
  
  venvDir = ".venv";
  
  shellHook = ''
    if [ ! -d "$venvDir" ]; then
      echo "Creating Python virtual environment..."
      ${pkgs.python313}/bin/python -m venv "$venvDir"
    fi
    
    echo "Activating virtual environment..."
    source "$venvDir"/bin/activate
    
    echo "Installing Python packages..."
    "$venvDir"/bin/python -m pip install -r requirements.txt
    
    echo "Using Python: $(which python)"
    echo "Using pip: $(which pip)"
    echo "Python version: $(python --version)"
  '';
}
