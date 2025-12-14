# goji/app/organization/services.py

from ..extensions import db
from .models import BusinessUnit, LegalEntity, FactoryCluster, Plant
from .schemas import (
    BusinessUnitSchema, 
    LegalEntitySchema, 
    FactoryClusterSchema, 
    PlantSchema
)
from marshmallow import ValidationError

class OrganizationService:
    """
    Encapsulates business logic for the Organization structure 
    (Business Units, Legal Entities, Clusters, Plants).
    """

    def __init__(self):
        # Instantiate schemas for validation and loading
        self.bu_schema = BusinessUnitSchema()
        self.le_schema = LegalEntitySchema()
        self.cluster_schema = FactoryClusterSchema()
        self.plant_schema = PlantSchema()

    # =========================================================
    # Business Unit Logic
    # =========================================================
    
    def get_all_business_units(self):
        return BusinessUnit.query.all()

    def create_business_unit(self, data: dict) -> BusinessUnit:
        try:
            new_bu = self.bu_schema.load(data)
            db.session.add(new_bu)
            db.session.commit()
            return new_bu
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # Legal Entity Logic
    # =========================================================

    def get_all_legal_entities(self):
        return LegalEntity.query.all()

    def create_legal_entity(self, data: dict) -> LegalEntity:
        try:
            new_le = self.le_schema.load(data)
            db.session.add(new_le)
            db.session.commit()
            return new_le
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # Factory Cluster Logic
    # =========================================================

    def get_all_clusters(self):
        return FactoryCluster.query.all()

    def create_cluster(self, data: dict) -> FactoryCluster:
        try:
            new_cluster = self.cluster_schema.load(data)
            db.session.add(new_cluster)
            db.session.commit()
            return new_cluster
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # Plant Logic
    # =========================================================

    def get_all_plants(self):
        return Plant.query.all()
    
    def get_plant_by_id(self, plant_id):
        return Plant.query.get_or_404(plant_id)

    def create_plant(self, data: dict) -> Plant:
        try:
            new_plant = self.plant_schema.load(data)
            db.session.add(new_plant)
            db.session.commit()
            return new_plant
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

# Singleton instance
org_service = OrganizationService()