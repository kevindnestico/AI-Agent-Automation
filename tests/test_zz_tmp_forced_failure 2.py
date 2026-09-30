from pages import InventoryPage


def test_forced_failure(inventory_page: InventoryPage):
    inventory_page.page.get_by_test_id("does-not-exist").click(timeout=1000)
