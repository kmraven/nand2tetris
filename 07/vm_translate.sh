# Translate all *.vm files to assembly code
find . -name "*.vm" | while read vm_file; do
    echo "Translating $vm_file to assembly code..."
    python main.py "$vm_file"
    if [ $? -ne 0 ]; then
        echo "Error translating $vm_file"
        exit 1
    fi
    echo "Translation of $vm_file completed."
done
