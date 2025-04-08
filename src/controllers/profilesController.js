const express = require('express');

const prisma = require('../utils/db.js');

const router = express.Router();


router.post('/', async (req, res, next) => {
    try {
        const { title, description, permissions } = req.body;

        const profile = await prisma.profile.create({
            data: {
                title,
                description,
            }
        });

        const foundPermissions = await prisma.permission.findMany({
            where: { permission: { in: permissions } },
        });

        await prisma.permissionsOnProfiles.createMany({
            data: foundPermissions.map((perm) => ({
                profileId: profile.id,
                permissionId: perm.id,
            })),
        });

        const profileWithPermissions = await prisma.profile.findUnique({
            where: { id: profile.id },
            include: {
                permissions: {
                    include: { permission: true },
                },
            },
        });

        return res.status(201).json(profileWithPermissions);
    } catch (error) {
        console.log(error);
        next(error);
    }
});


module.exports = router;