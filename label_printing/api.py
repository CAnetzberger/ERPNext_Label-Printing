from __future__ import unicode_literals

import frappe
import os
import json
from frappe import _

from PyPDF2 import PdfWriter


@frappe.whitelist()
def print_label(values):
    values = json.loads(values)

    print_format = frappe.get_value(
        "Label Printer", values["printer_select"], "label_print_format")

    for label in values["labels"]:
        doc = frappe.new_doc('Label')
        if "item_code" in values:
            doc.item_code = values["item_code"]
        if "item_name" in values:
            doc.item_name = values["item_name"]
        if "delivery_date" in values:
            doc.delivery_date = values["delivery_date"]
        if "customer" in values:
            doc.customer = values["customer"]
        if "batch" in values:
            doc.batch = values["batch"]
        if "item_qty" in label:
            doc.qty = label["item_qty"]
        if "information" in label:
            doc.information = label["information"]

        newdoc = doc.insert()

        print_label_by_server(
            "Label", newdoc.name, label["label_qty"], values["printer_select"], print_format, doc=None, no_letterhead=0, file_path=None)

    return 200


def print_label_by_server(doctype, name, qty, printer_setting, print_format=None, doc=None, no_letterhead=0, file_path=None):
    pdf_options = {
        'page-width': '{0}mm'.format(frappe.get_value("Label Printer", printer_setting, "label_width")),
        'page-height': '{0}mm'.format(frappe.get_value("Label Printer", printer_setting, "label_height")),
    }

    print_settings = frappe.get_doc(
        "Network Printer Settings", printer_setting)

    try:
        import cups
    except ImportError:
        frappe.throw(_("You need to install pycups to use this feature!"))

    try:
        cups.setServer(print_settings.server_ip)
        cups.setPort(print_settings.port)
        conn = cups.Connection()
        output = PdfWriter()
        output = frappe.get_print(doctype, name, print_format, doc=doc,
                                  no_letterhead=no_letterhead, as_pdf=True, output=output, pdf_options=pdf_options)
        if not file_path:
            file_path = os.path.join(
                "/", "tmp", f"frappe-pdf-{frappe.generate_hash()}.pdf")
            output.write(open(file_path, "wb"))
            for _ in range(qty):
                conn.printFile(print_settings.printer_name,
                               file_path, name, {})

    except OSError as e:
        if (
            "ContentNotFoundError" in e.message
            or "ContentOperationNotPermittedError" in e.message
            or "UnknownContentError" in e.message
            or "RemoteHostClosedError" in e.message
        ):
            frappe.throw(_("PDF generation failed"))
    except cups.IPPError:
        frappe.throw(_("Printing failed"))


@frappe.whitelist()
def get_associated_stockentry(workorder):
    return frappe.get_last_doc('Stock Entry', filters={"work_order": workorder})

# @frappe.whitelist()
# def get_label_printers():
#    label_printing_settings = frappe.get_doc('Label Printing Settings')
#    label_printer_names = []
#
#    for x in label_printing_settings.label_printers:
#        label_printer_names.append(x.label_printer)
#
#    return(label_printer_names)
