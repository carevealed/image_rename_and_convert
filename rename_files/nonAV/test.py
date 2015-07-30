__author__ = 'California Audio Visual Preservation Project'
# import NonAVModel
from NonAVModel import CompressionModes
from NonAVModel.Element import Element
from NonAVModel.Technical import Technical
from NonAVModel.Instantiation import Instantiation
from NonAVModel.Instantiations import Instantiations
from NonAVModel.AssetPart import AssetPart
from NonAVModel.Assets import Assets
from NonAVModel.DublinCore import DublinCore
from NonAVModel.DescriptionDocument import DescriptionDocument
from NonAVModel.CollectionReference import CollectionReference
e = Element(tag="title", data="sadfsadf", attributes={"asdfasd": "asd", "asaa": "vfvfv"})
e2 =Element(tag="creator", data="sadfsadf", attributes={"x": "d", "asaa": "vfvfv"})

# print(e)
e2.add_child(e)
# e3 = Model.Element(tag="DescriptionDocument", value=e)
# print(e2)
tech = Technical(fileFormat="wav", imageFormat="asdfasdf", width=34, height=355, colorBitDepth=4, compressionMode=CompressionModes.LOSSLESS)
tech.colorSpace = "2:2:2"
# tech.chromaSubsampling = "RGB"
tech.additionalTechnicalNotes = "asdfasdfasdfasdfasdfasdfasdfasdfasdf"
instantiation = Instantiation("asdfasdf")
instantiation.generation="afafafafafafafafafaf"
instantiation.checksum="asdfasdfasdf234"
instantiation.checksumType="md5"
instantiation.fileSize="423423"
instantiation.fileSizeUnit="megabytes"
instantiation.derivedFrom="cvcv"
instantiation.technical = tech.xml


instantiations = Instantiations()
instantiations.add_instantiation(instantiation.xml)
instantiations.relationship="asdfadfad"

assetPart = AssetPart(instantiations.xml)
# print(assetPart)


assets = Assets(object_id="sdfsfs", project_id="asdfasdf", color="browish")
assets.hasParts = "2 pages"
assets.additionalDescription = "I don't know what you have to say, it makes not difference anyway."
assets.assetPart = assetPart.xml
assets.physicalLocation = "Neverland"
# print(assets)
dublinCore = DublinCore(title="Shades of Anaheim - Family Portrait", creator="Betzsoldt Studio, Anaheim, California")
dublinCore.add_date("1930")
dublinCore.type = "Still Image"
dublinCore.add_identifier("asdfasdf", "barcode")
dublinCore.add_source("Anaheim Public Library", type="Owning instutution", url="http://www.sample.org")
dublinCore.add_coverage("Anaheim, California", type="Geographic")
dublinCore.add_date("2015", "Added")
dublinCore.rights = "Copyright status unknown. This work may be protected by the U.S. Copyright Law " \
					"(Title 17, U.S.C.). In addition, its reproduction may be restricted by terms of gift or " \
					"purchase agreements, donor restrictions, privacy and publicity rights, licensing and " \
					"trademarks. This work is accessible for purposes of education and research. Transmission or " \
					"reproduction of works protected by copyright beyond that allowed by fair use requires the " \
					"written permission of the copyright owners. Works not in the public domain cannot be " \
					"commercially exploited without permission of the copyright owner. Responsibility for any " \
					"use rests exclusively with the user. The California State Library attempted to find rights " \
					"owners without success but is eager to hear from them so that we may obtain permission, " \
					"if needed. Upon request to csllds@library.ca.gov digitized works can be removed " \
				    "from public view if there are rights issues that need to be resolved"

# print(dublinCore)
description_document = DescriptionDocument()
description_document.dublinCore=dublinCore.xml
description_document.assets=assets.xml
# print(description_document)

collection = CollectionReference(collectionSource="California State Library", projectSource="CAPS")
collection.descriptionDocument = description_document.xml
print(collection)
print("Done")
