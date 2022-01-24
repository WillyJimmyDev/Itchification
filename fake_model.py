from PySide2 import os


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_icon_path(name):
    p =os.path.join(CURRENT_DIR, "thumbnails", name)
    # print(p)
    return os.path.join(CURRENT_DIR, "thumbnails", name)

model_data = [
            
            {
                "title":"Hydrogen",
                "description": "Hydrogen is a chemical element with chemical symbol H and atomic number 1. With an atomic weight of 1.00794 u, hydrogen is the lightest element on the periodic table. Its monatomic form (H) is the most abundant chemical substance in the Universe, constituting roughly 75% of all baryonic mass.",
                "icon": get_icon_path("so.jpg"),
            },
            {
                "title":"Hydrogen",
                "description": "Hydrogen is a chemical element with chemical symbol H and atomic number 1. With an atomic weight of 1.00794 u, hydrogen is the lightest element on the periodic table. Its monatomic form (H) is the most abundant chemical substance in the Universe, constituting roughly 75% of all baryonic mass.",
                "icon": get_icon_path("so.jpg"),
            },
            
        
]