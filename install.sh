#!/bin/bash

# স্ক্রিপ্টটি যে ফোল্ডারে আছে, তার পাথ অটোমেটিকভাবে বের করবে (যাতে হার্ডকোড করতে না হয়)
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
COMMAND_NAME="cheat-sit"
BIN_PATH="$BIN_DIR/$COMMAND_NAME"

echo "⏳ Installing $COMMAND_NAME..."

# ১. ~/.local/bin ফোল্ডার না থাকলে তৈরি করে নেবে
mkdir -p "$BIN_DIR"

# ২. ডাইনামিকভাবে cheat-sit এক্সিকিউটেবল ফাইলটি তৈরি করা হচ্ছে
cat > "$BIN_PATH" <<EOF
#!/bin/bash

# রিপোজিটরির ডিরেক্টরিতে যাবে
cd "$REPO_DIR" || { echo "❌ Error: Directory $REPO_DIR not found."; exit 1; }

# GitHub থেকে অটো-আপডেট হবে (সাইলেন্টলি)
git pull origin main --quiet 2>/dev/null

# পাইথন স্ক্রিপ্ট রান করবে
python3 cheat-sit.py "\$@"
EOF

# ৩. ফাইলটিকে এক্সিকিউটেবল করা হচ্ছে
chmod +x "$BIN_PATH"

echo "✅ Installation successful!"
echo "🎉 You can now use the tool by typing: $COMMAND_NAME"
echo ""
echo "⚠️ Note: If '$COMMAND_NAME' command is not found, run 'source ~/.bashrc' or restart your terminal."
