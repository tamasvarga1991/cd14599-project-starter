import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#

def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    expected_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending"
    }

    mock_storage.save_order.assert_called_once_with(
        "ORD001",
        expected_order
    )


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")


def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    """Tests retrieving an existing order by its ID."""
    existing_order = {"order_id": "ORD001", "item_name": "Laptop"}
    mock_storage.get_order.return_value = existing_order

    result = order_tracker.get_order_by_id("ORD001")

    assert result == existing_order
    mock_storage.get_order.assert_called_once_with("ORD001")


def test_get_order_by_id_returns_none_if_order_does_not_exist(order_tracker, mock_storage):
    """Tests retrieving a non-existent order returns None."""
    result = order_tracker.get_order_by_id("ORD_MISSING")

    assert result is None
    mock_storage.get_order.assert_called_once_with("ORD_MISSING")


def test_get_order_by_id_raises_error_if_order_id_is_empty(order_tracker):
    """Tests an empty order ID raises a ValueError."""
    with pytest.raises(ValueError):
        order_tracker.get_order_by_id("")


def test_update_order_status_successfully(order_tracker, mock_storage):
    """Tests updating an order's status preserves its other details."""
    existing_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing_order
    expected_order = {**existing_order, "status": "shipped"}

    order_tracker.update_order_status("ORD001", "shipped")

    mock_storage.get_order.assert_called_once_with("ORD001")
    mock_storage.save_order.assert_called_once_with("ORD001", expected_order)


def test_update_order_status_raises_error_if_status_is_invalid(order_tracker, mock_storage):
    """Tests invalid statuses are rejected before accessing storage."""
    with pytest.raises(ValueError):
        order_tracker.update_order_status("ORD001", "invalid_status")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_raises_error_if_order_does_not_exist(order_tracker, mock_storage):
    """Tests updating a non-existent order raises a ValueError."""
    with pytest.raises(ValueError):
        order_tracker.update_order_status("ORD_MISSING", "shipped")

    mock_storage.get_order.assert_called_once_with("ORD_MISSING")
    mock_storage.save_order.assert_not_called()


def test_update_order_status_raises_error_if_order_id_is_empty(order_tracker):
    """Tests an empty order ID raises a ValueError."""
    with pytest.raises(ValueError):
        order_tracker.update_order_status("", "shipped")


def test_list_all_orders_returns_empty_list_if_storage_is_empty(order_tracker, mock_storage):
    """Tests empty storage returns an empty list."""
    mock_storage.get_all_orders.return_value = {}

    assert order_tracker.list_all_orders() == []


def test_list_all_orders_returns_multiple_orders(order_tracker, mock_storage):
    """Tests all stored orders are returned as a list."""
    first_order = {"order_id": "ORD001", "status": "pending"}
    second_order = {"order_id": "ORD002", "status": "shipped"}
    mock_storage.get_all_orders.return_value = {
        "ORD002": second_order,
        "ORD001": first_order,
    }

    result = order_tracker.list_all_orders()

    assert isinstance(result, list)
    assert sorted(result, key=lambda order: order["order_id"]) == [first_order, second_order]


def test_list_orders_by_status_returns_only_matching_orders(order_tracker, mock_storage):
    """Tests filtering returns all matching orders and excludes other statuses."""
    first_match = {"order_id": "ORD001", "status": "shipped"}
    second_match = {"order_id": "ORD003", "status": "shipped"}
    mock_storage.get_all_orders.return_value = {
        "ORD003": second_match,
        "ORD002": {"order_id": "ORD002", "status": "pending"},
        "ORD001": first_match,
    }

    result = order_tracker.list_orders_by_status("shipped")

    assert isinstance(result, list)
    assert sorted(result, key=lambda order: order["order_id"]) == [first_match, second_match]


def test_list_orders_by_status_returns_empty_list_if_no_matches(order_tracker, mock_storage):
    """Tests filtering returns an empty list when no stored orders match."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {"order_id": "ORD001", "status": "pending"},
    }

    assert order_tracker.list_orders_by_status("shipped") == []


def test_list_orders_by_status_raises_error_if_status_is_empty(order_tracker):
    """Tests an empty status raises a ValueError."""
    with pytest.raises(ValueError):
        order_tracker.list_orders_by_status("")


def test_list_orders_by_status_raises_error_if_status_is_invalid(order_tracker):
    """Tests an invalid status raises a ValueError."""
    with pytest.raises(ValueError):
        order_tracker.list_orders_by_status("invalid_status")
