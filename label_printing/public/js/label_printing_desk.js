$(document).ready(function () {
  $(".dropdown-notifications").after('<li id="labels-toolbar" class="nav-item"><a class="nav-link label-printing-icon text-muted"><i class="fa fa-tag fa-lg" aria-hidden="true"></i></a></li>');
  $("#labels-toolbar").click(function (page) {
    setupLabelsDialog(page);
  });

});



function setupLabelsDialog(page) {
  let cur_frm = page.view.cur_frm

  let fields = {
    labels: [{
      item_qty: 0,
      label_qty: 1
    }]
  };


  if (cur_frm !== null) {
    if (cur_frm.doctype === "Work Order" || cur_frm.doctype === "Item") {
      if (cur_frm.docname) {
        fields.doctype = cur_frm.doctype
        fields.docname = cur_frm.docname
      }
    }
  }

  let label_printer_names

  let d = new frappe.ui.Dialog({
    title: __("Print Labels"),
    fields: [{
      label: __("Reference Doctype"),
      options: ['Work Order', 'Item', 'Label'],
      fieldname: 'doctype',
      fieldtype: 'Select',
      default: fields.doctype,
    },
    {
      label: __("Get data"),
      fieldname: 'get_data',
      fieldtype: 'Button',
      click: () => {
        handleDataFetch()
      }
    },
    {
      fieldtype: 'Column Break'
    },
    {
      label: __("Reference Docname"),
      fieldname: 'docname',
      fieldtype: 'Data',
      options: 'doctype',
      default: fields.docname,
    },
    {
      fieldtype: 'Section Break',
      label: __('Information')
    },
    {
      label: __("Item Code"),
      fieldname: 'item_code',
      fieldtype: 'Data'
    },
    {
      label: __("Item Name"),
      fieldname: 'item_name',
      fieldtype: 'Data'
    },
    {
      label: __("Delivery Date"),
      fieldname: 'delivery_date',
      fieldtype: 'Date'
    },
    {
      fieldtype: 'Column Break'
    },
    {
      label: __("Customer"),
      fieldname: 'customer',
      fieldtype: 'Data'
    },
    {
      label: __("Batch"),
      fieldname: 'batch',
      fieldtype: 'Data'
    },
    {
      fieldtype: 'Section Break',
      label: __('Printer')
    },
    {
      label: __("Printer Select"),
      options: ['Labeldrucker Werk 1 (Ind. 6)', 'Labeldrucker Werk 2 (Bre. 19)'],
      fieldname: 'printer_select',
      fieldtype: 'Select',
      default: 'Labeldrucker Werk 1 (Ind. 6)'
    },
    {
      fieldtype: 'Section Break',
      label: __('Labels')
    },
    {
      fieldname: "labels",
      fieldtype: "Table",
      cannot_add_rows: false,
      in_place_edit: true,
      data: fields.labels,
      get_data: () => {
        return fields.labels;
      },
      fields: [{
        fieldtype: 'Int',
        fieldname: "item_qty",
        in_list_view: 1,
        label: __('Item Qty')
      },
      {
        label: __("Label Qty"),
        fieldname: 'label_qty',
        in_list_view: 1,
        fieldtype: 'Int'
      },
      {
        fieldtype: 'Data',
        fieldname: "information",
        in_list_view: 1,
        label: __('Information')
      },
      ]
    },
    ],
    primary_action_label: 'Print',
    primary_action(values) {
      frappe.call({
        method: "label_printing.api.print_label",
        args: {
          values: values
        },
        callback: function (r) {
          if (r.message === 200) {
            frappe.show_alert("Label printing successful", 5);
          }
        },
      });

      d.hide();

    }
  });
  handleDataFetch();
  d.show();


  // handle dpctype change
  d.fields_dict.doctype.$input.on('change', function () {
    d.fields_dict.docname.refresh();
  });

  function handleDataFetch() {
    fields = d.get_values()
    if (fields.doctype && fields.docname) {
      let doc = get_doc(fields.doctype, fields.docname)
      if (fields.doctype === "Work Order") {
        let item = get_doc("Item", doc.production_item)
        let se = 1
        frappe.call({
          method: "label_printing.api.get_associated_stockentry",
          async: false,
          args: { workorder: fields.docname },
          callback(r) {
            if (r.message) {
              fields.batch = r.message.items[r.message.items.length - 1].batch_no
            }
          }
        })
        fields.item_code = item.item_code
        fields.item_name = item.item_name
        fields.delivery_date = doc.expected_delivery_date
        fields.labels[0].item_qty = doc.qty
        fields.labels[0].label_qty = 1

        if (item.associated_company) {
          let customer = get_doc("Customer", item.associated_company)
          if (customer.short_name) {
            fields.customer = customer.short_name
          } else {
            fields.customer = item.associated_company
          }
        }

        fields.total_amount = doc.qty
        d.fields_dict.labels.refresh();

      } else if (fields.doctype === "Item") {
        let item = get_doc("Item", doc.item_code)

        fields.item_code = doc.item_code
        fields.item_name = doc.item_name

        if (item.associated_company) {
          let customer = get_doc("Customer", doc.associated_company)
          if (customer.short_name) {
            fields.customer = customer.short_name
          } else {
            fields.customer = doc.associated_company
          }
        }
      }
      d.set_values(fields)
    }
  }

}

function get_doc(doctype, docname) {
  let res;
  frappe.call({
    method: "frappe.client.get",
    async: false,
    args: {
      doctype: doctype,
      name: docname,
    },
    callback(r) {
      if (r.message) {
        res = r.message
      }
    }
  });
  return res;
}