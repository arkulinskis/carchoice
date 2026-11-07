import anvil.media
import anvil.server
from anvil import *

from ._anvil_designer import DataTabTemplate
from ... import catalog, state

MODES = [("Update them and add new ones", "merge"), ("Leave them, only add new ones", "add")]


class DataTab(DataTabTemplate):
    """Admin -> Car data: import a CSV (file or pasted), check it first, see what each import did and undo one,
    download all the data or an empty template."""

    def __init__(self, **properties):
        super().__init__(**properties)
        self.file = None
        self.mode_dd.items = MODES
        self.mode_dd.selected_value = "merge"
        state.set_control_attr(self.mode_dd, "aria-label", "Cars already in the table")
        state.set_control_attr(self.paste_box, "aria-label", "Paste CSV rows")
        self.result_box.visible = False
        self.imports_panel.add_event_handler("x-undo", self._undo)
        self._log()

    def _log(self):
        self.imports_panel.items = state.call("admin_imports")["imports"]

    def _input(self):
        if self.file is not None:
            return self.file
        text = self.paste_box.text or ""
        if not text.strip():
            state.toast("Choose a CSV file or paste some rows first.", "error")
            return None
        return text

    @handle("file_loader", "change")
    def file_loader_change(self, file=None, **event_args):
        self.file = file
        self.file_name.text = ("Ready: %s (%s KB)" % (file.name, max(1, int(file.length / 1024)))) if file else ""
        self.result_box.visible = False

    def _show(self, title, p, imported=None):
        self.result_box.visible = True
        self.result_title.text = title
        lines = ["%d rows read, %d usable." % (p["rows"], p["readable"])]
        if imported:
            lines.append("%d cars added, %d updated." % (imported["added"], imported["updated"]))
        else:
            lines.append("%d new cars, %d updates%s." % (p["new"], p["updates"], (", %d skipped (already there)" % p["skipped"]) if p["skipped"] else ""))
        if p["new_makes"]:
            lines.append("New brands: " + ", ".join(p["new_makes"]) + ".")
        if p["new_fields"]:
            lines.append("New fields (filters + columns): " + ", ".join("%s (%s)" % (f["label"], f["kind"]) for f in p["new_fields"]) + ".")
        if p["sample"]:
            lines.append("First rows: " + ", ".join(p["sample"]) + ".")
        self.result_text.text = "\n".join(lines)
        errs = p["errors"]
        self.result_errors.text = ("Problems (these rows or cells were skipped):\n" + "\n".join(errs)) if errs else ""
        self.result_errors.visible = bool(errs)

    @handle("preview_button", "click")
    def preview_button_click(self, **event_args):
        src = self._input()
        if src is None:
            return
        r = state.call("admin_import_preview", src, self.mode_dd.selected_value)
        if r is not None:
            self._show("Check: nothing has changed yet", r["preview"])

    @handle("import_button", "click")
    def import_button_click(self, **event_args):
        src = self._input()
        if src is None:
            return
        name = self.file.name if self.file is not None else "Pasted data"
        r = state.call("admin_import", src, name, self.source_box.text or "", self.mode_dd.selected_value)
        if r is None:
            return
        res = r["result"]
        self._show("Imported", res, res)
        state.toast("Imported: %d added, %d updated." % (res["added"], res["updated"]), "ok")
        catalog.forget()
        self.file = None
        self.file_loader.clear()
        self.file_name.text = ""
        self.paste_box.text = ""
        self._log()

    def _undo(self, item, **event_args):
        if confirm("The %d cars this import added leave the catalogue (and people's fives). Changes it made to cars that "
                   "were already there stay." % item["still_here"], title="Undo %s?" % item["filename"],
                   buttons=[("Cancel", False), ("Remove them", True)], role="app-dialog"):
            r = state.call("admin_undo_import", item["id"])
            if r is not None:
                state.toast("%d cars removed." % r["removed"], "ok")
                catalog.forget()
                self._log()

    def _download(self, template):
        r = state.call("admin_export_csv", template)
        if r is not None:
            anvil.media.download(BlobMedia("text/csv", r["csv"].encode("utf-8"), name=r["filename"]))

    @handle("export_button", "click")
    def export_button_click(self, **event_args):
        self._download(False)

    @handle("template_button", "click")
    def template_button_click(self, **event_args):
        self._download(True)
