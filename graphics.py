from project_util.artefact.artefact import Artefact


class Graphics:
    @staticmethod
    def save_image(data, file_name, superres: int = 0):
        artefact = Artefact(
            name=file_name,
            project=self.project,
            data=data,
        )
        artefact.save()
        if superres:
            superres_artefact = artefact.get_superres(
                superres,
                new_project=self.project.add_folder(f"x{superres}"),
            )
            artefact.save()
            superres_artefact.save(self.project)
