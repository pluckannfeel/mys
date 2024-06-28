document.addEventListener('DOMContentLoaded', function() {
    gsap.registerPlugin(ScrollTrigger);

    gsap.from('.introduction', {
        opacity: 0,
        y: 50,
        duration: 1,
        ease: 'power2.out'
    });

    const teamMembers = document.querySelector('.team-members');
    const teamMemberWidth = document.querySelector('.team-member').offsetWidth;
    const teamMemberCount = document.querySelectorAll('.team-member').length;

    // Clone the team members to create an infinite loop effect
    for (let i = 0; i < teamMemberCount; i++) {
        const clone = teamMembers.children[i].cloneNode(true);
        teamMembers.appendChild(clone);
    }

    const totalWidth = teamMemberWidth * teamMembers.children.length;

    // Create an infinite horizontal scroll
    gsap.to('.team-members', {
        x: `-=${teamMemberWidth * teamMemberCount}`,
        ease: 'none',
        duration: teamMemberCount * 5, // Adjust speed here
        repeat: -1,
        modifiers: {
            x: gsap.utils.unitize(x => parseFloat(x) % (teamMemberWidth * teamMemberCount)) // Seamlessly loop the scroll
        }
    });

    document.querySelectorAll('.team-member').forEach(member => {
        const img = member.querySelector('.team-member-img');
        const hoverImg = member.querySelector('.team-member-hover-img');

        gsap.set(hoverImg, { opacity: 0 });

        member.addEventListener('mouseenter', function() {
            gsap.to(img, { opacity: 0, duration: 0.15, ease: 'power2.inOut' });
            gsap.to(hoverImg, { opacity: 1, duration: 0.15, ease: 'power2.inOut' });
        });
        member.addEventListener('mouseleave', function() {
            gsap.to(img, { opacity: 1, duration: 0.15, ease: 'power2.inOut' });
            gsap.to(hoverImg, { opacity: 0, duration: 0.15, ease: 'power2.inOut' });
        });
    });
});