openerp.help_shortcut = function(instance) {
	instance.web.UserMenu.include({
		on_menu_help: function() {
			window.open('http://10.56.8.242/help/index.html', '_blank');
		},
	});
};