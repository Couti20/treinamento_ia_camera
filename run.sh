#!/bin/bash
# Script para rodar o EPI Detector em tempo real

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       🎥 EPI DETECTOR - SISTEMA DE MONITORAMENTO           ║"
echo "║          Detecção de Pessoas e Equipamentos de             ║"
echo "║            Proteção em Tempo Real via Câmera               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar se modelo existe
if [ ! -f "yolov8n.pt" ] && [ ! -f "best.pt" ]; then
    echo "❌ Erro: Nenhum modelo encontrado!"
    echo "   Coloque yolov8n.pt ou best.pt no diretório raiz"
    exit 1
fi

echo "✓ Configuração validada"
echo "✓ Câmera: /dev/video0 (webcam)"
echo "✓ Confiança: 0.3 (30%)"
echo "✓ Performance: ~0.7 FPS em CPU (normal)"
echo ""

echo "📊 OPÇÕES DE USO:"
echo ""
echo "1️⃣  TEMPO REAL COM GUI (pressione Q para sair):"
echo "   python main.py"
echo ""
echo "2️⃣  TESTE SEM GUI (salva vídeo anotado em logs/):"
echo "   python test_video_output.py"
echo ""
echo "3️⃣  VER LOGS DE DETECÇÕES:"
echo "   head -20 logs/ppe_audit.csv"
echo ""
echo "4️⃣  EXIBIR VÍDEO SALVO:"
echo "   ffplay logs/test_output.mp4  # ou VLC, etc"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Iniciando sistema em tempo real..."
echo ""
echo "Controles:"
echo "  • Q / ESC: Sair"
echo "  • Pressione Ctrl+C se preso"
echo ""

python main.py
