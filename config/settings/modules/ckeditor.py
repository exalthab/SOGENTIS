# config/settings/modules/ckeditor.py

from django.conf import settings

CKEDITOR_5_UPLOAD_PATH = "uploads/ckeditor/"

CKEDITOR_5_CONFIGS = {
    "default": {
        "language": "fr",
        "height": 300,
        "width": "100%",

        "toolbar": [
            "heading",
            "|",
            "bold", "italic", "underline", "strikethrough",
            "|",
            "link",
            "|",
            "bulletedList", "numberedList",
            "|",
            "blockQuote",
            "|",
            "insertTable",
            "insertTable",
            "imageUpload",
            "|",
            "undo", "redo",
        ],

        "heading": {
            "options": [
                {"model": "paragraph", "title": "Paragraphe"},
                {"model": "heading2", "view": "h2", "title": "Titre 2"},
                {"model": "heading3", "view": "h3", "title": "Titre 3"},
            ]
        },

        "image": {
            "toolbar": [
                "imageTextAlternative",
                "imageStyle:full",
                "imageStyle:side",
                "imageStyle:alignLeft",
                "imageStyle:alignRight",
                "imageStyle:alignCenter",
            ]
        },

        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
            ]
        },
    }
}

