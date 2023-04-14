from sqlmodel import SQLModel, Session, create_engine, Field
import stock_items as stock_items
import stock_locations as stock_locations

class data_manager:
    def initialize_database():
        stock_items.import_all_stock_items()
        stock_locations.import_all_locations()

    def add_stock_item(si_code: str, name: str):
        stock_items.add_stock_item(si_code=si_code, name=name)
    
    def add_stock_location(si_code: str, name: str):
        stock_locations.add_stock_location(si_code=si_code, name=name)
