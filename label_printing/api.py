from __future__ import unicode_literals

import frappe, os
import json
from frappe import _


from frappe.utils.pdf import get_pdf,cleanup
from frappe.core.doctype.access_log.access_log import make_access_log
from PyPDF2 import PdfFileWriter


@frappe.whitelist()
def print_label(values):
    values = json.loads(values)
    printer_setting = frappe.db.get_single_value('Label Printer Settings', 'label_printer'),


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
        if "qty" in label:
            doc.qty = label["item_qty"]
        if "information" in label:
            doc.information = label["information"]
        newdoc = doc.insert()

        print_label_by_server("Label", newdoc.name, label["label_qty"], printer_setting[0],"Label", doc=None, no_letterhead=0, file_path=None)

    return 200
    

def print_label_by_server(doctype, name, qty, printer_setting, print_format=None, doc=None, no_letterhead=0, file_path=None):
    pdf_options = {
        'page-height': frappe.db.get_single_value('Label Printer Settings', 'label_height'),
        'page-width': frappe.db.get_single_value('Label Printer Settings', 'label_width'),
    }
    print_settings = frappe.get_doc("Network Printer Settings", printer_setting)
    try:
        import cups
    except ImportError:
        frappe.throw(_("You need to install pycups to use this feature!"))

    try:
        cups.setServer(print_settings.server_ip)
        cups.setPort(print_settings.port)
        conn = cups.Connection()
        output = PdfFileWriter()
        output = frappe.get_print(doctype, name, print_format, doc=doc, no_letterhead=no_letterhead, as_pdf = True, output = output, pdf_options=pdf_options)
        print("Here")
        print(output)
        if not file_path:
            file_path = os.path.join("/", "tmp", "frappe-pdf-{0}.pdf".format(frappe.generate_hash()))
        output.write(open(file_path,"wb"))
        for _ in range(qty):
            conn.printFile(print_settings.printer_name,file_path , name, {})
    except IOError as e:
        if ("ContentNotFoundError" in e.message
            or "ContentOperationNotPermittedError" in e.message
            or "UnknownContentError" in e.message
            or "RemoteHostClosedError" in e.message):
            frappe.throw(_("PDF generation failed"))
    except cups.IPPError:
        frappe.throw(_("Printing failed"))
    finally:
        return


@frappe.whitelist()
def get_associated_stockentry(workorder):
    return frappe.get_last_doc('Stock Entry', filters = {"work_order": workorder})