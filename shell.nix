{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    spotipy
    python-dotenv
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pythonEnv
  ];

  shellHook = ''
    echo "========================================================="
    echo " Spotify Sorter Development Environment Loaded (NixOS)"
    echo "========================================================="
    echo "Python:   $(python --version)"
    echo "Packages: spotipy, python-dotenv"
    echo ""
    echo "Run 'python spotify_sorter.py' to launch the interactive menu."
    echo "========================================================="
  '';
}
