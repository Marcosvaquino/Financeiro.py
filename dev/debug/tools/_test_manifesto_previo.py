import sys
from pathlib import Path
from openpyxl import Workbook

# ensure workspace on path
workspace = str(Path(__file__).resolve().parents[1])
if workspace not in sys.path:
    sys.path.insert(0, workspace)

uploads = Path('financeiro') / 'uploads' / 'frete'
uploads.mkdir(parents=True, exist_ok=True)

orig_name = 'PREVIA MANIFESTO 1 QZ SETEMBRIO.xlsx'
save_path = uploads / orig_name

# create minimal workbook
wb = Workbook()
ws = wb.active
ws['A1'] = 'Tipo'
wb.save(str(save_path))

print('Saved test original file:', save_path)

# Now simulate the import handler effect by calling the flask upload logic is hard; instead mimic rename logic here
# We'll import the module to reuse logic
from financeiro import frete

# Simulate what importacao route does: detect and move
mf_base = 'Manifesto_Frete'
ext = save_path.suffix
manifest_name = f"{mf_base}{ext}"
manifest_path = uploads / manifest_name
# remove if exists
if manifest_path.exists():
    manifest_path.unlink()
# perform rename (as import handler would)
save_path.replace(manifest_path)
print('Renamed to:', manifest_path)

# List uploads folder
print('\nUploads folder:')
for f in sorted(uploads.iterdir()):
    print('-', f.name)