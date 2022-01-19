import frappe


@frappe.whitelist()
def create_labels(values):
    print(values)
    return 200
