class MultiDBRouter:
    def db_for_read(self, model, **hints):
        """
        Direct read operations to the appropriate database.
        """
        if model._meta.app_label == "mysknv":
            return "mysknv"
        if model._meta.app_label == "fred":
            return "fred"
        return "default"

    def db_for_write(self, model, **hints):
        """
        Direct write operations to the appropriate database.
        """
        if model._meta.app_label == "mysknv":
            return "mysknv"
        if model._meta.app_label == "fred":
            return "fred"
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow any relation if both objects are in the same database.
        """
        db_set = {"default", "fred", "mysknv"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations only apply to the appropriate database.
        """
        if app_label == "mysknv":
            return db == "mysknv"
        if app_label == "fred":
            return db == "fred"
        return db == "default"
