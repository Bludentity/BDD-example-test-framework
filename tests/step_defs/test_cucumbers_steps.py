from cucumbers import CucumberBasket
from pytest_bdd import scenarios, given, when, then, parsers
from functools import partial
import pytest
import logging


CONVERTERS = {
    'initial': int,
    'count': int,
    'total': int
}

scenarios('../features/cucumbers.feature')

EXTRA_TYPES = {
    'Number': int
}

parse_num = partial(parsers.cfparse, extra_types=EXTRA_TYPES)


@pytest.fixture
def basket():
    logging.info("Creating a new empty basket")
    return CucumberBasket(initial_count=0)


@given(parse_num('the basket has "{initial:Number}" cucumbers'))
@given('the basket has "<initial>" cucumbers')
def basket_has_cucumbers(basket, initial):
    logging.info(f"Setting up basket with {initial} cucumbers")
    try:
        basket.add(initial)
        logging.info(f"Successfully added {initial} cucumbers to the basket")
    except Exception as error:
        logging.error(f"Failed to add {initial} cucumbers: {str(error)}")
        raise
    return basket


@when(parse_num('"{count:Number}" cucumbers are added to the basket'))
@when('"<count>" cucumbers are added to the basket')
def add_cucumbers(basket, count):
    current_count = basket.count
    logging.info(f"Adding {count} cucumbers to the basket (current: {current_count})")
    try:
        basket.add(count)
        logging.info(f"Successfully added {count} cucumbers. New count: {basket.count}")
    except Exception as error:
        logging.error(f"Failed to add {count} cucumbers: {str(error)}")
        raise


@when(parse_num('"{count:Number}" cucumbers are removed from the basket'))
@when('"<count>" cucumbers are removed from the basket')
def remove_cucumbers(basket, count):
    current_count = basket.count
    try:
        basket.remove(count)
        logging.info(f"Successfully removed {count} cucumbers. New count: {basket.count}")
    except ValueError as error:
        logging.error(f"Failed to remove {count} cucumbers: {str(error)}")
        raise


@then(parse_num('the basket contains "{total:Number}" cucumbers'))
@then('the basket contains "<total>" cucumbers')
def basket_has_total_cucumbers(basket, total):
    actual_count = basket.count
    logging.info(f"Verifying basket contains {total} cucumbers (actual: {actual_count})")
    try:
        assert actual_count == total, f"Expected {total} cucumbers but found {actual_count}"
        logging.info("Basket count verification successful")
    except AssertionError as error:
        logging.error(f"Basket count verification failed: {str(error)}")
        raise