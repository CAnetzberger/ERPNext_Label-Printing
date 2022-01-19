import frappe
from frappe.utils.print_format import print_by_server
import json


@frappe.whitelist()
def create_labels(values):

    values = json.loads(values)
    print(values)

    print(values["item_code"])

    doc = frappe.new_doc('Label')
    doc.item_code = values["item_code"]
    doc.item_name = values["item_name"]

    res = doc.insert(ignore_permissions=True,  # ignore write permissions during insert
                     ignore_links=True,  # ignore Link validation in the document
                     ignore_if_duplicate=True,  # dont insert if DuplicateEntryError is thrown
                     ignore_mandatory=True  # insert even if mandatory fields are not set
                     )
    print(res)

    # print_by_server("Label", "Label-00001", "labelprinter", "Labels")
    return 200
