from numpy import datetime64

from openfisca_france.model.base import Individu, Variable, MONTH, date, TypesActivite, TypesStatutOccupationLogement, Menage


class date_entree_logement(Variable):
    value_type = date
    default_value = date(1970, 1, 1)
    entity = Menage
    definition_period = MONTH
    label = "Date entrée dans le logement"


class mon_job_mon_logement_eligibilite_logement(Variable):
    value_type = bool
    entity = Individu
    definition_period = MONTH
    label = "Eligibilité logement de l'aide mon jon mon logement"

    def formula(individu, period):
        statut_occupation_logement = individu.menage('statut_occupation_logement', period)
        locataire = ((statut_occupation_logement == TypesStatutOccupationLogement.locataire_hlm)
                     + (statut_occupation_logement == TypesStatutOccupationLogement.locataire_vide)
                     + (statut_occupation_logement == TypesStatutOccupationLogement.locataire_meuble))
        return locataire * (individu.menage('date_entree_logement', period) > datetime64(period.offset(-3, 'month').start))


class mon_job_mon_logement_eligibilite_jeunes_actifs(Variable):
    value_type = bool
    entity = Individu
    definition_period = MONTH
    label = "Éligibilité à l'aide mon job mon logement pour les jeunes actifs"

    def formula(individu, period):
        eligibilite_activite = (individu('activite', period) == TypesActivite.actif) + individu('alternant', period)
        smic_mensuel_brut = individu("smic_proratise", period)
        eligibilite_salaire = (individu("salaire_de_base", period) <= smic_mensuel_brut) * (individu("salaire_de_base", period) >= smic_mensuel_brut * 0.3)
        eligibilite_logement = individu('mon_job_mon_logement_eligibilite_logement', period)
        eligibilite_activite_debut = individu('contrat_de_travail_debut', period) > datetime64(period.offset(-6, 'month').start)
        elibilite_age = individu('age', period) < 25

        return eligibilite_activite * eligibilite_salaire * eligibilite_logement * eligibilite_activite_debut * elibilite_age


class mon_job_mon_logement_eligibilite(Variable):
    value_type = bool
    entity = Individu
    definition_period = MONTH
    label = "Éligibilité à l'aide mon job mon logement"

    def formula(individu, period):
        eligibilite_activite = (individu('activite', period) == TypesActivite.actif) + individu('alternant', period)
        smic_mensuel_brut = individu("smic_proratise", period)
        eligibilite_salaire = individu("salaire_de_base", period) <= smic_mensuel_brut * 1.5
        eligibilite_logement = individu('mon_job_mon_logement_eligibilite_logement', period)
        eligibilite_activite_debut = individu('contrat_de_travail_debut', period) >= datetime64(
            period.offset(-3, 'month').start)

        return eligibilite_activite * eligibilite_salaire * eligibilite_logement * eligibilite_activite_debut


class mon_job_mon_logement(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH
    label = "Montant de l'aide mon job mon logement"
    reference = ["https://www.actionlogement.fr/aide-mon-job-mon-logement"]

    def formula(individu, period, parameters):
        montant = parameters(period).prestations.mon_job_mon_logement.montant
        eligibilite = individu('mon_job_mon_logement_eligibilite', period) + individu('mon_job_mon_logement_eligibilite_jeunes_actifs', period)
        return montant * eligibilite
