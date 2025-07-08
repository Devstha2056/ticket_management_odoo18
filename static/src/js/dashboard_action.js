/** @odoo-module */
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted } = owl;
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

export class CustomDashBoard extends Component {

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        onWillStart(this.onWillStart);
        onMounted(this.onMounted);
    }

    async onWillStart() {
        await this.fetch_data();
    }

    async onMounted() {
        // Optional: Code to run after component is mounted
    }

    async fetch_data() {
        const result = await rpc('/web/dataset/call_kw/ticket.management/get_details', {
            model: 'ticket.management',
            method: 'get_details',
            args: [{}],
            kwargs: {},
        });

        // Store values in separate variables to avoid overwriting functions
        this.total_tickets_count = result['total_tickets'];
        this.total_open_count = result['total_open'];
        this.total_wip_count = result['total_wip'];
        this.total_wot_count = result['total_wot'];
        this.total_closed_count = result['total_closed'];
        this.total_staff_count = result['staff'];
        this.total_urgent_count = result['total_urgent'];
        this.total_high_count = result['total_high'];
        this.total_medium_count = result['total_medium'];
        this.total_low_count = result['total_low'];
    }

    // Button click handler for Total Tickets
    total_tickets(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Total Ticket"),
            type: 'ir.actions.act_window',
            res_model: 'ticket.management',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            target: 'current'
        }, options);
    }
    total_open(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Open Tickets"),
            type: 'ir.actions.act_window',
            res_model: 'ticket.management',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
             domain: [['state', '=', 'open']],
            target: 'current'
        }, options);
    }
     total_closed(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Closed Tickets"),
            type: 'ir.actions.act_window',
            res_model: 'ticket.management',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
             domain: [['state', '=', 'closed']],
            target: 'current'
        }, options);
    }
    total_wip(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Wip Tickets"),
            type: 'ir.actions.act_window',
            res_model: 'ticket.management',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
             domain: [['state', '=', 'work_in']],
            target: 'current'
        }, options);
    }

    total_wot(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Work Delivered Tickets"),
            type: 'ir.actions.act_window',
            res_model: 'ticket.management',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
             domain: [['state', '=', 'work_out']],
            target: 'current'
        }, options);
    }
    staff(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Staff"),
            type: 'ir.actions.act_window',
            res_model: 'res.users',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: [['groups_id.name', 'in',['Admin','Employee','User']]],
            target: 'current'
        }, options);
    }
     total_urgent(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Total urgent Tickets"),
            type: 'ir.actions.act_window',
            res_model: 'ticket.management',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
             domain: [['priority', '=', 'urgent']],
            target: 'current'
        }, options);
    }
     total_high(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Total High Tickets"),
            type: 'ir.actions.act_window',
            res_model: 'ticket.management',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
             domain: [['priority', '=', 'high']],
            target: 'current'
        }, options);
    }
     total_medium(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Total Medium Tickets"),
            type: 'ir.actions.act_window',
            res_model: 'ticket.management',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
             domain: [['priority', '=', 'medium']],
            target: 'current'
        }, options);
    }
     total_low(e) {
        e.stopPropagation();
        e.preventDefault();
        const options = { on_reverse_breadcrum: this.on_reverse_breadcrum };
        this.action.doAction({
            name: _t("Total Low Tickets"),
            type: 'ir.actions.act_window',
            res_model: 'ticket.management',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
             domain: [['priority', '=', 'low']],
            target: 'current'
        }, options);
    }
}

CustomDashBoard.template = "CustomDashBoard";
registry.category("actions").add("custom_dashboard_tags", CustomDashBoard);
