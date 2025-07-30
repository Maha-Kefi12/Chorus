import json
from pathlib import Path
from jinja2 import Environment
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

# === Chemins des fichiers ===
function_name_path = Path(resource_path(r"output\function-name-f.json"))
response_json_path = Path(resource_path(r"output\response.json"))
base_output_dir = Path(resource_path(r".idea\demo"))

# === Lecture du functionName depuis function-name.json ===
with function_name_path.open(encoding="utf-8") as f:
    function_data = json.load(f)

function_name = function_data.get("functionName", "").strip()
if not function_name:
    raise ValueError("❌ 'functionName' introuvable dans function-name.json")

# ✅ Définir function_id ici
function_id = f"{function_name}IRap"

# === Lecture du premier formId réel depuis response.json ===
with response_json_path.open(encoding="utf-8") as f:
    response_data = json.load(f)

form_id = None
for key in response_data:
    if key.lower() not in ["default", "ridtins"]:
        form_id = key
        break

if not form_id:
    raise ValueError("❌ Aucun formId réel trouvé dans response.json")

# === Créer un sous-dossier avec le nom du form_id ===
output_subfolder = base_output_dir / form_id
output_subfolder.mkdir(parents=True, exist_ok=True)

# === Définir le chemin du fichier XML ===
screen_xml_path = output_subfolder / f"{function_id}.screen.xml"

# === Objet "function" attendu par le template (non utilisé ici, juste pour info)
function = {
    "id": f"{function_name}IRap",
    "beanId": f"{function_name}ScreenService",
    "icon": "icons/kate.png",
    "graphic": {
        "headerVisible": "true",
        "borderVisible": "true"
    },
    "forms": [
        {
            "sortNumber": "1",
            "id": form_id,
            "editable": "true",
            "fatherId": form_id,
            "graphic": {
                "borderVisible": "true",
                "fieldSetMode": "true"
            }
        }
    ],
    "screenActions": [
        {
            "id": "launch",
            "code": "launchAini",
            "icon": "edition",
            "evaluateControls": "true",
            "actionResponses": {
                "onSuccess": {
                    "refreshScreens": {
                        "functionIds": [f"{function_name}IRap"]
                    }
                }
            }
        }
    ]
}

# === Template XML Jinja2 ===
template_content = """<?xml version="1.0" encoding="UTF-8"?>
<function xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="http://scheme.cf.linedata.com/function.xsd"
          type="create"
          id="{{ function_name }}IRap"
          beanId="{{ function_name }}ScreenService"
          icon="icons/kate.png">

  <graphic>
    <headerVisible>true</headerVisible>
    <borderVisible>true</borderVisible>
  </graphic>

  <form sortNumber="1"
        id="{{ form_id }}"
        editable="true"
        fatherId="{{ father_id }}">
    <graphic>
      <borderVisible>true</borderVisible>
      <fieldSetMode>true</fieldSetMode>
    </graphic>
  </form>

  <screenActions>
    <screenAction id="launch{{ function_name }}" code="launch{{ function_name }}" icon="edition" evaluateControls="true">
      <actionResponses>
        <onSuccess>
          <refreshScreens>
            <functionIds>
              <functionId>{{ function_name }}IRap</functionId>
            </functionIds>
          </refreshScreens>
        </onSuccess>
      </actionResponses>
    </screenAction>
  </screenActions>

</function>
"""

# === Rendu avec Jinja2 ===
env = Environment()
template = env.from_string(template_content)
rendered_xml = template.render(
    function_name=function_name,
    form_id=form_id,
    father_id=f"{form_id}BlockForm"
)

# === Écriture du fichier XML ===
screen_xml_path.write_text(rendered_xml, encoding="utf-8")
print(f"✅ XML généré avec succès : {screen_xml_path}")
