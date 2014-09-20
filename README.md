# Description
Le Social Network Harvester (SNH) est un outil qui permet d'archiver le contenu de plusieurs sites de réseaux sociaux 
dans le but d'analyser le comportement des utilisateurs. Il est en mesure d'archiver le contenu provenant des réseaux 
Facebook, Twitter, Youtube et Dailymotion.

# Technologies requises
* Apache
* MySQL
* [python](https://www.python.org/)
* [django](https://www.djangoproject.com/)
* [python-twitter](https://github.com/bear/python-twitter)
* [fandjango](https://github.com/jgorset/fandjango)
* [gdata](https://code.google.com/p/gdata-python-client/)
* [Twitter registered app](https://apps.twitter.com/)
* [Facebook registered app](https://developers.facebook.com/apps/)

# Technologies optionnelles
* [virtualenv](http://warpedtimes.wordpress.com/2012/09/23/a-tutorial-on-virtualenv-to-isolate-python-installations/)

# Outils pour le développement
* [Facebook Graph API explorer](https://developers.facebook.com/tools/explorer)
* [Facebook access token debug](https://developers.facebook.com/tools/accesstoken/)
* [Facebook Graph API - User](https://developers.facebook.com/docs/graph-api/reference/v2.1/user)
* [Facebook API migration](https://developers.facebook.com/docs/apps/migrations)
* [Twitter doc](https://dev.twitter.com/overview/documentation)
* [Twitter REST API console](https://dev.twitter.com/rest/public)

# Installation
Pour installer le SNH, consulter la page suivante: [Installation](https://github.com/pylanglois/Social-Network-Harvester/wiki/Installation).

# Vue d'ensemble
Le diagramme suivant montre l'architecture générale du SNH. Il se divise en 2 grandes sections, soit le noyau qui 
aspire le contenu des réseaux sociaux et les vues web qui permettent aux chercheurs de gérer l'outil et d'accéder 
aux données.

![Architecture du SNH](http://i.imgur.com/oovmVtv.png)

## SNH core, aspiration des données
Chaque réseau social utilise un modèle de données qui lui est particulier. Afin de simplifier le développement, 
le modèle de données du SNH est calqué sur celui de chaque réseau. 

Les deux prochaines images montrent l'évolution du résultat d'une requête du format JSON, en passant par l'objet 
python-twitter pour terminer dans une classe du modèle du SNH.

![JSON2PYTHON](http://i.imgur.com/qSfdLeQ.png)

![PT2TWstatut](http://i.imgur.com/4iFq2MK.png)

Les deux prochaines images montrent une version simplifiée des relations pour les modèles de données Facebook et 
Twitter du SNH

![FBModel](http://i.imgur.com/PIOzO07.png)

![TWModel](http://i.imgur.com/At0YWkt.png)

### Facebook, access_token
Afin d'effectuer des requêtes sur le Graph API, le serveur doit obtenir un jeton de sécurité qui permet de définir le 
périmètre d'accès de l'application. Par exemple, un jeton généré avec l'utilisateur Pierre donnera accès au mur de 
Pierre, mais pas au mur de Simon, à moins que Simon et Pierre soient amis. La définition du périmètre est proposée à 
l'utilisateur lors de la génération du jeton (accès au mur, accès à la liste d'amis, etc.)

Les jetons ont une date d'expiration et doivent être renouvelés régulièrement. Les jetons de type utilisateurs ont 
généralement une durée d'une heure. Pour une application web, il est nécessaire de demander un "extended token" qui 
lui aura une durée de 60 jours. Il est primordial de surveiller l'échéance de la date d'expiration afin de ne pas 
manquer le renouvellement!

Voir [Access Token](https://developers.facebook.com/docs/facebook-login/access-tokens)

### Facebook, batch
Lorsqu'un grand volume de données doit être aspiré, il est nécessaire d'effectuer des requêtes en parallèle afin d'être 
en mesure d'aspirer l'ensemble du contenu. Facebook offre cette possibilité grâce à l'appel "batch".
Lorsque l'on effectue une requête simple, par exemple pour obtenir tous les statuts d'un mur, le Graph API limite la 
quantité de résultats à un sous-ensemble limité à 250 éléments. Afin d'obtenir les 250 éléments suivants, une nouvelle 
requête sera nécessaire. Voici à quoi ressemble la structure JSON retournée à la suite d'une requête simple: 
[pastebin](http://pastebin.com/M6mKzpGr). Vous remarquerez que la dernière partie du la structure JSON contient un 
élément nommé paging. Cet élément contient la prochaine requête à appeler afin d'obtenir la suite des éléments.

Dans le cas d'un appel de type "batch", le même principe est utilisé. La seule différence est qu'il est possible 
d'inclure jusqu'à 50 requêtes dans un seul appel d'API. Voici un exemple avec 2 requêtes: 
[batch request](http://pastebin.com/ciTmE0Af). Le résultat obtenu sera similaire à une requête simple, mais structuré 
en liste de résultats. Voir [Batch Request](https://developers.facebook.com/docs/graph-api/making-multiple-requests)

L'algorithme d'aspiration contenu dans le FacebookHarvester utilise cette possibilité. Une liste d'appel "à faire" est 
construite au fur et à mesure que les résultats sont obtenus (bman_obj). À chaque tour d'appel à l'API, cette liste est 
utilisée pour remplir la commande "batch" avec 50 nouvelles requêtes. Voici un exemple d'un appel de type "batch" pour 
un seul utilisateur:

1. Obtenir les infos de l'utilisateur
1. Obtenir les 250 premiers statuts du mur de l'utilisateur
1. Analyser le résultat obtenu et déduire les nouvelles requêtes suivantes
  + Obtenir les 250 statuts suivants
  + Lire le premier statut reçu et déduire les requêtes suivantes:
    + Obtenir les 250 premiers likes
    + Obtenir les 250 premiers commentaires

### Facebook, gestion des erreurs
Une bonne gestion des erreurs est primordiale au succès d'une aspiration efficace. Malheureusement, les erreurs 
retournées ne sont pas toujours cohérentes. Certains batch doivent parfois être abandonnés pour ne pas bloquer 
l'aspiration. Parfois une seule requête problématique peut faire échouer un batch complet. C'est pourquoi il est 
nécessaire d'isoler les requêtes problématiques pour éviter de les insérer dans une requête groupée.

Voici quelques exemples pour vous faire la main!

* liberalquebec/feed?limit=500
* liberalquebec/feed?limit=250
* jlmelenchon/feed?limit=250

### Facebook, versions de l'API
![Mise à jour du Graph API](https://pbs.twimg.com/media/BxdAsQlCYAAmXU2.png)

Comme montré dans le diagramme d'architecture ci-haut ([Architecture du SNH](http://i.imgur.com/oovmVtv.png)) le code
du SNH est en contact direct avec l'API de facebook. Cela implique qu'une modification à l'API implique une mise à jour
du code. À l'heure où cette documentation est écrite, le SNH supporte à la version 1.0 de l'API, qui sera débranché
le 30 avril 2015. Une mise à jour du code est donc nécessaire afin de rendre compatible le SNH à nouvelle version de 
l'API.

* [Graph API upgrade](https://developers.facebook.com/docs/apps/upgrading)
* [Graph API versioning](https://developers.facebook.com/docs/apps/versions)