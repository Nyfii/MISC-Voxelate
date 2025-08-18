{ pkgs ? import <nixpkgs> {} }:

let
  pythonWithVenv = pkgs.python3.withPackages (ps: [
    ps.virtualenv
  ]);
in

pkgs.mkShell {
  buildInputs = [
    pythonWithVenv
  ];

  # The name of our virtual environment directory
  venvDir = ".venv";

  shellHook = ''
    # Create the virtual environment if it doesn't exist
    if [ ! -d "$venvDir" ]; then
      echo "Creating Python virtual environment..."
      ${pythonWithVenv}/bin/python -m venv "$venvDir"
    fi

    # Activate the virtual environment
    echo "Activating virtual environment..."
    source "$venvDir"/bin/activate

    pip install fake-bpy-module-latest
  '';
}
