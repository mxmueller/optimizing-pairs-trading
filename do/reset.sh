#!/bin/bash

# Funktion zur Anzeige der Hilfe
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Docker cleanup script"
    echo ""
    echo "Options:"
    echo "  --all    Führt vollständige Bereinigung durch (Container, Volumes, Images)"
    echo "  --help   Zeigt diese Hilfe an"
}

# Wenn keine Parameter übergeben wurden
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Parameter verarbeiten
while [ "$1" != "" ]; do
    case $1 in
        --all )
            echo "Führe vollständige Docker-Bereinigung durch..."

            echo "1. Stoppe alle Container und entferne Volumes und Images..."
            docker compose down --volumes --rmi all

            echo "2. Führe System Prune durch..."
            # Automatisches "yes" mit -y Flag
            docker system prune -af --volumes

            echo "Bereinigung abgeschlossen!"
            ;;
        --help )
            show_help
            exit
            ;;
        * )
            echo "Unbekannte Option: $1"
            show_help
            exit 1
    esac
    shift
done